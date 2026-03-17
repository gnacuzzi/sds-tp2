#ifndef PARTICLE_H
#define PARTICLE_H

typedef struct {
    int id;
    double x;
    double y;
    double vx;
    double vy;
    double angle;
    int is_leader;
} Particle;

#endif
