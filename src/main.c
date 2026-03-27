#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#include "cim.h"
#include "generator.h"
#include "io.h"
#include "particle.h"

#define STATIC_FILE "output/static.txt"
#define DYNAMIC_FILE "output/dynamic.txt"
#define DYNAMIC_CORRELATION_FILE "output/dynamic_correlation.txt"
#define DYNAMIC_MEAN_ANGLE_FILE "output/dynamic_mean_angle.txt"
#define VA_FILE "output/va.txt"

#define L_DEFAULT 10.0
#define RHO_DEFAULT 4.0
#define RC_DEFAULT 1.0
#define SPEED_DEFAULT 0.03
#define DT_DEFAULT 1.0
#define ETA_DEFAULT 0.0
#define STEPS_DEFAULT 2000
#define OUTPUT_EVERY 1
#define VA_EVERY 1
/* N = rho * L^2 = 4 * 10^2 = 400 */
#define N_DEFAULT ((int)(RHO_DEFAULT * L_DEFAULT * L_DEFAULT))

#define LEADER_RADIUS_DEFAULT 5.0
#define LEADER_CX_DEFAULT 5.0
#define LEADER_CY_DEFAULT 5.0

/*
 * Criterio CIM:
 *   L / M > rc
 * Con L = 10 y rc = 1, M = 9 cumple:
 *   10 / 9 > 1
 */
#define M_DEFAULT 9

static int **allocate_int_matrix(int rows, int cols) {
    int **matrix = malloc(rows * sizeof(int *));
    if (matrix == NULL) {
        return NULL;
    }

    for (int i = 0; i < rows; i++) {
        matrix[i] = malloc(cols * sizeof(int));
        if (matrix[i] == NULL) {
            for (int j = 0; j < i; j++) {
                free(matrix[j]);
            }
            free(matrix);
            return NULL;
        }
    }

    return matrix;
}

static void free_int_matrix(int **matrix, int rows) {
    if (matrix == NULL) {
        return;
    }

    for (int i = 0; i < rows; i++) {
        free(matrix[i]);
    }
    free(matrix);
}

static double random_uniform(double min, double max) {
    return min + (max - min) * ((double)rand() / (double)RAND_MAX);
}

static double wrap_position(double value, double L) {
    while (value < 0.0) {
        value += L;
    }
    while (value >= L) {
        value -= L;
    }
    return value;
}

static double compute_order_parameter(Particle *particles, int n, double speed) {
    double sum_vx = 0.0;
    double sum_vy = 0.0;

    for (int i = 0; i < n; i++) {
        sum_vx += particles[i].vx;
        sum_vy += particles[i].vy;
    }

    return sqrt(sum_vx * sum_vx + sum_vy * sum_vy) / (n * speed);
}

/*
 * Caso 0: sin líder
 *
 * SUPUESTO:
 * - La propia partícula se incluye en el promedio angular.
 * - El ruido es uniforme en [-eta/2, eta/2].
 * - Actualización sincrónica: se escribe en next_particles.
 */
static void update_particles_no_leader(Particle *particles, Particle *next_particles, int n,
                                       double L, double speed, double dt, double eta,
                                       int **neighbors, int *neighbor_count) {
    for (int i = 0; i < n; i++) {
        double sum_cos = cos(particles[i].angle);
        double sum_sin = sin(particles[i].angle);

        int particle_neighbors_count = neighbor_count[i];

        for (int k = 0; k < particle_neighbors_count; k++) {
            int j = neighbors[i][k];
            sum_cos += cos(particles[j].angle);
            sum_sin += sin(particles[j].angle);
        }

        double avg_angle = atan2(sum_sin / (particle_neighbors_count + 1),
                                 sum_cos / (particle_neighbors_count + 1));
        double noise = random_uniform(-eta / 2.0, eta / 2.0);
        double new_angle = avg_angle + noise;

        double new_vx = speed * cos(new_angle);
        double new_vy = speed * sin(new_angle);

        next_particles[i].id = particles[i].id;
        next_particles[i].is_leader = 0;
        next_particles[i].angle = new_angle;
        next_particles[i].vx = new_vx;
        next_particles[i].vy = new_vy;
        next_particles[i].x = wrap_position(particles[i].x + new_vx * dt, L);
        next_particles[i].y = wrap_position(particles[i].y + new_vy * dt, L);
    }
}

static void update_particles_fixed_leader(Particle *particles, Particle *next_particles, int n,
                                          double L, double speed, double dt, double eta,
                                          int **neighbors, int *neighbor_count) {
    for (int i = 0; i < n; i++) {
        if (particles[i].is_leader) {
            next_particles[i].id = particles[i].id;
            next_particles[i].is_leader = 1;
            next_particles[i].angle = particles[i].angle;
            next_particles[i].vx = speed * cos(particles[i].angle);
            next_particles[i].vy = speed * sin(particles[i].angle);
            next_particles[i].x = wrap_position(particles[i].x + next_particles[i].vx * dt, L);
            next_particles[i].y = wrap_position(particles[i].y + next_particles[i].vy * dt, L);
            continue;
        }

        double sum_cos = cos(particles[i].angle);
        double sum_sin = sin(particles[i].angle);

        int particle_neighbors_count = neighbor_count[i];

        for (int k = 0; k < particle_neighbors_count; k++) {
            int j = neighbors[i][k];
            sum_cos += cos(particles[j].angle);
            sum_sin += sin(particles[j].angle);
        }

        double avg_angle = atan2(sum_sin / (particle_neighbors_count + 1),
                                 sum_cos / (particle_neighbors_count + 1));

        double noise = random_uniform(-eta / 2.0, eta / 2.0);
        double new_angle = avg_angle + noise;

        next_particles[i].id = particles[i].id;
        next_particles[i].is_leader = 0;
        next_particles[i].angle = new_angle;
        next_particles[i].vx = speed * cos(new_angle);
        next_particles[i].vy = speed * sin(new_angle);
        next_particles[i].x = wrap_position(particles[i].x + next_particles[i].vx * dt, L);
        next_particles[i].y = wrap_position(particles[i].y + next_particles[i].vy * dt, L);
    }
}

static void update_particles_circular_leader(Particle *particles, Particle *next_particles, int n,
                                             double L, double speed, double dt, double eta,
                                             int **neighbors, int *neighbor_count, double cx,
                                             double cy, double radius) {
    double omega = speed / radius;

    for (int i = 0; i < n; i++) {
        if (particles[i].is_leader) {
            double dx = particles[i].x - cx;
            double dy = particles[i].y - cy;
            double phi = atan2(dy, dx);
            double new_phi = phi + omega * dt;

            next_particles[i].id = particles[i].id;
            next_particles[i].is_leader = 1;

            next_particles[i].x = cx + radius * cos(new_phi);
            next_particles[i].y = cy + radius * sin(new_phi);

            /* velocidad tangente antihoraria */
            next_particles[i].angle = new_phi + M_PI / 2.0;
            next_particles[i].vx = speed * cos(next_particles[i].angle);
            next_particles[i].vy = speed * sin(next_particles[i].angle);
            continue;
        }

        double sum_cos = cos(particles[i].angle);
        double sum_sin = sin(particles[i].angle);

        int particle_neighbors_count = neighbor_count[i];

        for (int k = 0; k < particle_neighbors_count; k++) {
            int j = neighbors[i][k];
            sum_cos += cos(particles[j].angle);
            sum_sin += sin(particles[j].angle);
        }

        double avg_angle = atan2(sum_sin / (particle_neighbors_count + 1),
                                 sum_cos / (particle_neighbors_count + 1));
        double noise = random_uniform(-eta / 2.0, eta / 2.0);
        double new_angle = avg_angle + noise;

        next_particles[i].id = particles[i].id;
        next_particles[i].is_leader = 0;
        next_particles[i].angle = new_angle;
        next_particles[i].vx = speed * cos(new_angle);
        next_particles[i].vy = speed * sin(new_angle);
        next_particles[i].x = wrap_position(particles[i].x + next_particles[i].vx * dt, L);
        next_particles[i].y = wrap_position(particles[i].y + next_particles[i].vy * dt, L);
    }
}

static void initialize_fixed_leader(Particle *particles, double speed) {
    particles[0].is_leader = 1;
    particles[0].angle = 0.0;
    particles[0].vx = speed * cos(particles[0].angle);
    particles[0].vy = speed * sin(particles[0].angle);
}

static void initialize_circular_leader(Particle *particles, double speed, double cx, double cy,
                                       double radius) {
    double phi = 0.0;

    particles[0].is_leader = 1;
    particles[0].x = cx + radius * cos(phi);
    particles[0].y = cy + radius * sin(phi);

    /* tangente antihoraria */
    particles[0].angle = phi + M_PI / 2.0;
    particles[0].vx = speed * cos(particles[0].angle);
    particles[0].vy = speed * sin(particles[0].angle);
}

static void copy_particles(Particle *dest, Particle *src, int n) {
    for (int i = 0; i < n; i++) {
        dest[i] = src[i];
    }
}

static void print_usage(const char *program_name) {
    fprintf(stderr, "Uso: %s <leader_mode> <eta>\n", program_name);
    fprintf(stderr, "  leader_mode = 0  -> sin lider\n");
    fprintf(stderr,
            "  leader_mode = 1  -> lider de direccion fija (todavia no "
            "implementado)\n");
    fprintf(stderr, "  leader_mode = 2  -> lider circular (todavia no implementado)\n");
    fprintf(stderr, "  eta = ruido angular uniforme en [-eta/2, eta/2]\n");
}

int main(int argc, char *argv[]) {
    const int n = N_DEFAULT;
    const double L = L_DEFAULT;
    const double rc = RC_DEFAULT;
    const double speed = SPEED_DEFAULT;
    const double dt = DT_DEFAULT;
    const int steps = STEPS_DEFAULT;
    const int M = M_DEFAULT;

    int leader_mode = 0;
    double eta = ETA_DEFAULT;

    if (argc != 3) {
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }

    leader_mode = atoi(argv[1]);
    eta = atof(argv[2]);

    if (leader_mode < 0 || leader_mode > 2) {
        fprintf(stderr, "Error: leader_mode debe ser 0, 1 o 2.\n");
        print_usage(argv[0]);
        return EXIT_FAILURE;
    }

    if (eta < 0.0) {
        fprintf(stderr, "Error: eta debe ser >= 0.\n");
        return EXIT_FAILURE;
    }

    if ((L / M) <= rc) {
        fprintf(stderr, "Error: no se cumple el criterio del CIM: L / M > rc\n");
        fprintf(stderr, "L = %.3f, M = %d, rc = %.3f, L/M = %.3f\n", L, M, rc, L / M);
        return EXIT_FAILURE;
    }

    init_random_seed();

    Particle *particles = generate_particles(n, L, speed);
    if (particles == NULL) {
        fprintf(stderr, "Error generating particles.\n");
        return EXIT_FAILURE;
    }

    if (leader_mode == 1) {
        initialize_fixed_leader(particles, speed);
    } else if (leader_mode == 2) {
        initialize_circular_leader(
            particles, speed, LEADER_CX_DEFAULT, LEADER_CY_DEFAULT, LEADER_RADIUS_DEFAULT);
    }

    Particle *next_particles = malloc(n * sizeof(Particle));
    if (next_particles == NULL) {
        fprintf(stderr, "Error allocating next_particles.\n");
        free(particles);
        return EXIT_FAILURE;
    }

    int **neighbors = allocate_int_matrix(n, n - 1);
    if (neighbors == NULL) {
        fprintf(stderr, "Error allocating neighbors matrix.\n");
        free(next_particles);
        free(particles);
        return EXIT_FAILURE;
    }

    int *neighbor_count = malloc(n * sizeof(int));
    if (neighbor_count == NULL) {
        fprintf(stderr, "Error allocating neighbor_count.\n");
        free_int_matrix(neighbors, n);
        free(next_particles);
        free(particles);
        return EXIT_FAILURE;
    }

    write_static_file(STATIC_FILE, n, L, rc, speed, eta, leader_mode);
    clear_dynamic_file(DYNAMIC_FILE);
    clear_dynamic_file(VA_FILE);
    clear_dynamic_file(DYNAMIC_CORRELATION_FILE);
    clear_dynamic_file(DYNAMIC_MEAN_ANGLE_FILE);
    append_dynamic_frame(DYNAMIC_FILE, particles, n, 0.0);
    // append_correlation_frame(DYNAMIC_CORRELATION_FILE, 0.0, 0.0);
    // append_mean_angle_frame(DYNAMIC_MEAN_ANGLE_FILE, 0.0, 0.0);

    for (int step = 1; step <= steps; step++) {
        cim_neighbors(particles, n, L, M, rc, neighbors, neighbor_count);

        if (leader_mode == 0) {
            update_particles_no_leader(
                particles, next_particles, n, L, speed, dt, eta, neighbors, neighbor_count);
        } else if (leader_mode == 1) {
            update_particles_fixed_leader(
                particles, next_particles, n, L, speed, dt, eta, neighbors, neighbor_count);
        } else if (leader_mode == 2) {
            update_particles_circular_leader(particles,
                                             next_particles,
                                             n,
                                             L,
                                             speed,
                                             dt,
                                             eta,
                                             neighbors,
                                             neighbor_count,
                                             LEADER_CX_DEFAULT,
                                             LEADER_CY_DEFAULT,
                                             LEADER_RADIUS_DEFAULT);
        }

        copy_particles(particles, next_particles, n);

        if (step % OUTPUT_EVERY == 0) {
            append_dynamic_frame(DYNAMIC_FILE, particles, n, step * dt);
        }

        if (step % OUTPUT_EVERY == 0) {
            double sum_cos = 0.0;
            double sum_sen = 0.0;
            double leader_angle = 0.0;
            for (int i = 0; i < n; i++) {
                Particle particle = particles[i];
                if (!particle.is_leader) {
                    sum_cos += cos(particle.angle);
                    sum_sen += sin(particle.angle);
                } else {
                    leader_angle = particle.angle;
                }
            }

            double theta_s = atan2(sum_sen / (n - 1), sum_cos / (n - 1));
            double c = cos(leader_angle - theta_s);

            double t = step * dt;
            append_mean_angle_frame(DYNAMIC_MEAN_ANGLE_FILE, theta_s, t);
            append_correlation_frame(DYNAMIC_CORRELATION_FILE, c, t);
        }

        if (step % VA_EVERY == 0 || step == 1 || step == steps) {
            double va = compute_order_parameter(particles, n, speed);
            append_va_value(VA_FILE, va, step * dt);
            printf("step=%d  t=%.2f  va=%.6f\n", step, step * dt, va);
        }
    }

    free(neighbor_count);
    free_int_matrix(neighbors, n);
    free(next_particles);
    free(particles);

    return EXIT_SUCCESS;
}
