#!/bin/bash

LEADER=0

# Loop desde 1.3 hasta 5.0 con paso 0.1
for eta in $(seq 0.0 0.1 5.0)
do
    # Formatear a 1 decimal (importante para nombres consistentes)
    eta_fmt=$(printf "%.1f" $eta)

    echo ">>> Ejecutando ETA=$eta_fmt"

    make run LEADER=$LEADER ETA=$eta_fmt && \
    python3 python/va_chart.py output/va.txt $LEADER $eta_fmt && \
    python3 python/correlation.py c_t_ruido_$eta_fmt $LEADER

done