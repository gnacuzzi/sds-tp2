#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <time.h>

#include "generator.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static double random_uniform(double min, double max) {
    return min + (max - min) * ((double) rand() / (double) RAND_MAX);
}

void init_random_seed(void) {
    srand((unsigned int) time(NULL));
}

Particle *generate_particles(int n, double L, double speed) {
    Particle *particles = malloc(n * sizeof(Particle));
    if (particles == NULL) {
        fprintf(stderr, "Error allocating particles\n");
        return NULL;
    }

    for (int i = 0; i < n; i++) {
        double angle = random_uniform(0.0, 2.0 * M_PI);

        particles[i].id = i;
        particles[i].x = random_uniform(0.0, L);
        particles[i].y = random_uniform(0.0, L);
        particles[i].angle = angle;
        particles[i].vx = speed * cos(angle);
        particles[i].vy = speed * sin(angle);
        particles[i].is_leader = 0;
    }

    return particles;
}
