#ifndef GEOMETRY_H
#define GEOMETRY_H

#include "particle.h"

double center_distance(Particle p1, Particle p2, double L);

int are_neighbors(Particle p1, Particle p2, double rc, double L);

#endif
