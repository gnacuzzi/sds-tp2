#include <stdlib.h>
#include <stdio.h>

#include "cim.h"
#include "geometry.h"

typedef struct {
    int *particle_indices;
    int count;
    int capacity;
} Cell;

static void initialize_neighbor_counts(int *neighbor_count, int n) {
    for (int i = 0; i < n; i++) {
        neighbor_count[i] = 0;
    }
}

static Cell **create_grid(int M) {
    Cell **grid = malloc(M * sizeof(Cell *));
    if (grid == NULL) {
        return NULL;
    }

    for (int i = 0; i < M; i++) {
        grid[i] = malloc(M * sizeof(Cell));
        if (grid[i] == NULL) {
            for (int k = 0; k < i; k++) {
                free(grid[k]);
            }
            free(grid);
            return NULL;
        }

        for (int j = 0; j < M; j++) {
            grid[i][j].particle_indices = NULL;
            grid[i][j].count = 0;
            grid[i][j].capacity = 0;
        }
    }

    return grid;
}

static void free_grid(Cell **grid, int M) {
    if (grid == NULL) {
        return;
    }

    for (int i = 0; i < M; i++) {
        for (int j = 0; j < M; j++) {
            free(grid[i][j].particle_indices);
        }
        free(grid[i]);
    }
    free(grid);
}

static int append_to_cell(Cell *cell, int particle_index) {
    if (cell->count == cell->capacity) {
        int new_capacity = (cell->capacity == 0) ? 4 : cell->capacity * 2;
        int *new_indices = realloc(cell->particle_indices, new_capacity * sizeof(int));
        if (new_indices == NULL) {
            return 0;
        }

        cell->particle_indices = new_indices;
        cell->capacity = new_capacity;
    }

    cell->particle_indices[cell->count] = particle_index;
    cell->count++;

    return 1;
}

static void get_cell_indices(Particle p, double cell_size, int M, int *cx, int *cy) {
    *cx = (int)(p.x / cell_size);
    *cy = (int)(p.y / cell_size);

    if (*cx >= M) {
        *cx = M - 1;
    }
    if (*cy >= M) {
        *cy = M - 1;
    }
}

static int populate_grid(Cell **grid, Particle *particles, int n, double L, int M) {
    double cell_size = L / M;

    for (int i = 0; i < n; i++) {
        int cx, cy;
        get_cell_indices(particles[i], cell_size, M, &cx, &cy);

        if (!append_to_cell(&grid[cx][cy], i)) {
            return 0;
        }
    }

    return 1;
}

static void add_neighbor_pair(int **neighbors, int *neighbor_count, int i, int j) {
    neighbors[i][neighbor_count[i]] = j;
    neighbor_count[i]++;

    neighbors[j][neighbor_count[j]] = i;
    neighbor_count[j]++;
}


void cim_neighbors(
    Particle *particles,
    int n,
    double L,
    int M,
    double rc,
    int **neighbors,
    int *neighbor_count
) {
    initialize_neighbor_counts(neighbor_count, n);

    Cell **grid = create_grid(M);
    if (grid == NULL) {
        fprintf(stderr, "Error creating grid\n");
        return;
    }

    if (!populate_grid(grid, particles, n, L, M)) {
        fprintf(stderr, "Error populating grid\n");
        free_grid(grid, M);
        return;
    }

    int offsets[5][2] = {
        {0, 0},
        {1, 0},
        {0, 1},
        {1, 1},
        {-1, 1}
    };

    for (int cx = 0; cx < M; cx++) {
        for (int cy = 0; cy < M; cy++) {
            Cell current = grid[cx][cy];

            for (int o = 0; o < 5; o++) {
                int nx = (cx + offsets[o][0] + M) % M;
                int ny = (cy + offsets[o][1] + M) % M;

                Cell other = grid[nx][ny];

                if (offsets[o][0] == 0 && offsets[o][1] == 0) {
                    for (int i = 0; i < current.count; i++) {
                        for (int j = i + 1; j < current.count; j++) {
                            int pi = current.particle_indices[i];
                            int pj = current.particle_indices[j];

                            if (are_neighbors(particles[pi], particles[pj], rc, L)) {
                                add_neighbor_pair(neighbors, neighbor_count, pi, pj);
                            }
                        }
                    }
                } else {
                    for (int i = 0; i < current.count; i++) {
                        for (int j = 0; j < other.count; j++) {
                            int pi = current.particle_indices[i];
                            int pj = other.particle_indices[j];

                            if (are_neighbors(particles[pi], particles[pj], rc, L)) {
                                add_neighbor_pair(neighbors, neighbor_count, pi, pj);
                            }
                        }
                    }
                }
            }
        }
    }

    free_grid(grid, M);
}
