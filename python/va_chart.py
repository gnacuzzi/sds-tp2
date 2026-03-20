import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import sys
import numpy as np

# uso: python script.py X step
if len(sys.argv) != 3:
    print("Uso: python script.py <X> <step_ticks>")
    sys.exit(1)

X = float(sys.argv[1])
step = float(sys.argv[2])

x = []
y = []

# Leer archivo
with open('output/va.txt', 'r') as f:
    for line in f:
        if line.strip():
            t, v = map(float, line.split())
            x.append(t)
            y.append(v)

# Filtrar datos desde X
x_filtrado = [t for t in x if t >= X]
y_filtrado = [v for t, v in zip(x, y) if t >= X]

if len(y_filtrado) == 0:
    print(f"No hay datos para t >= {X}")
    sys.exit(1)

# Calcular promedio y desvío desde X
promedio = np.mean(y_filtrado)
desvio = np.std(y_filtrado)

print(f"Para t >= {X}:")
print(f"Promedio = {promedio}")
print(f"Desvío estándar = {desvio}")

# Graficar datos
plt.figure()
plt.plot(x, y, marker='o', markersize=3, label='Datos')

ax = plt.gca()
ax.xaxis.set_major_locator(MultipleLocator(step))

# Línea horizontal del promedio solo desde X
plt.plot(
    [X, max(x_filtrado)],
    [promedio, promedio],
    linestyle='--',
    label=f'Promedio = {promedio:.4f}'
)

# Banda de desvío solo desde X
plt.fill_between(
    x_filtrado,
    promedio - desvio,
    promedio + desvio,
    alpha=0.2,
    label=f'± Desvío ({desvio:.4f})'
)

# Línea vertical para marcar X
plt.axvline(X, linestyle=':', label=f'X = {X}')

plt.xlabel('Tiempo')
plt.ylabel('v_a')
plt.title('v_a en función del tiempo')

plt.legend()
plt.grid()
plt.show()