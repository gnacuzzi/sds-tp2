#include <math.h>

#include "geometry.h"

double center_distance(Particle p1, Particle p2, double L) {
    double dx = p1.x - p2.x;
    double dy = p1.y - p2.y;

    dx = dx - L * round(dx / L);
    dy = dy - L * round(dy / L);

    return sqrt(dx * dx + dy * dy);
}

int are_neighbors(Particle p1, Particle p2, double rc, double L) {
    return center_distance(p1, p2, L) < rc;
}
