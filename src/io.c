#include <stdio.h>
#include <stdlib.h>

#include "io.h"

void write_static_file(const char *filename, int n, double L, double rc,
                       double v, double eta, int leader_mode) {
    FILE *file = fopen(filename, "w");

    if (file == NULL) {
        fprintf(stderr, "Error opening static file %s\n", filename);
        return;
    }

    fprintf(file, "%d\n", n);
    fprintf(file, "%.6f\n", L);
    fprintf(file, "%.6f\n", rc);
    fprintf(file, "%.6f\n", v);
    fprintf(file, "%.6f\n", eta);
    fprintf(file, "%d\n", leader_mode);

    fclose(file);
}

void clear_dynamic_file(const char *filename) {
    FILE *file = fopen(filename, "w");

    if (file == NULL) {
        fprintf(stderr, "Error clearing dynamic file %s\n", filename);
        return;
    }

    fclose(file);
}

void append_dynamic_frame(const char *filename, Particle *particles, int n, double t) {
    FILE *file = fopen(filename, "a");

    if (file == NULL) {
        fprintf(stderr, "Error opening dynamic file %s\n", filename);
        return;
    }

    fprintf(file, "%.6f\n", t);

    for (int i = 0; i < n; i++) {
        fprintf(file, "%.6f %.6f %.6f %.6f %d\n",
                particles[i].x,
                particles[i].y,
                particles[i].vx,
                particles[i].vy,
                particles[i].is_leader);
    }

    fclose(file);
}
