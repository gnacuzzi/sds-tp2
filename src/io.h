#ifndef IO_H
#define IO_H

#include "particle.h"

void write_static_file(const char *filename, int n, double L, double rc,
                       double v, double eta, int leader_mode);

void clear_dynamic_file(const char *filename);

void append_dynamic_frame(const char *filename, Particle *particles, int n, double t);

void append_va_value(const char * filename, double va, double t);

#endif
