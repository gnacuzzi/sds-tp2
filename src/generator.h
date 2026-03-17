#ifndef GENERATOR_H
#define GENERATOR_H

#include "particle.h"

void init_random_seed(void);
Particle *generate_particles(int n, double L, double speed);

#endif
