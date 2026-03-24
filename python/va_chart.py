import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# =========================
# Configuración tipográfica
# =========================
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.unicode_minus'] = False

# =========================
# Parámetro: nombre de salida
# =========================
if len(sys.argv) != 2:
    print("Uso: python script.py <nombre_salida>")
    sys.exit(1)

nombre_salida = sys.argv[1]

# =========================
# Parámetros fijos
# =========================
X = 0          # desde dónde calcular promedio y desvío
STEP_X = 200   # separación fija de ticks en eje X

# =========================
# Lectura de datos
# =========================
x = []
y = []

with open('output/va.txt', 'r') as f:
    for line in f:
        if line.strip():
            t, v = map(float, line.split())
            x.append(t)
            y.append(v)

if len(x) == 0:
    print("El archivo output/va.txt está vacío o no contiene datos válidos.")
    sys.exit(1)

# =========================
# Filtrado desde X
# =========================
x_filtrado = [t for t in x if t >= X]
y_filtrado = [v for t, v in zip(x, y) if t >= X]

if len(y_filtrado) == 0:
    print(f"No hay datos para t >= {X}")
    sys.exit(1)

# =========================
# Estadísticas
# =========================
promedio = np.mean(y_filtrado)
desvio = np.std(y_filtrado)

print(f"Para t >= {X}:")
print(f"Promedio = {promedio}")
print(f"Desvío estándar = {desvio}")

# =========================
# Crear carpeta de salida
# =========================
os.makedirs("graphics", exist_ok=True)

ruta_salida = os.path.join("graphics", f"{nombre_salida}.png")
ruta_txt = os.path.join("graphics", f"{nombre_salida}.txt")

# =========================
# Guardar TXT
# =========================
with open(ruta_txt, "w") as f:
    f.write(f"nombre_imagen: {nombre_salida}.png\n")
    f.write(f"promedio: {promedio}\n")
    f.write(f"desvio: {desvio}\n")

print(f"Datos guardados en: {ruta_txt}")

# =========================
# Gráfico
# =========================
fig, ax = plt.subplots(figsize=(10, 6))

# Línea + puntos en todos los valores
ax.plot(
    x,
    y,
    linestyle='-',
    linewidth=1.0,
    marker='o',
    markersize=3,
    label=r'$v_a(t)$'
)

# Ticks del eje X cada 200
ax.xaxis.set_major_locator(MultipleLocator(STEP_X))

# Promedio
ax.plot(
    [X, max(x_filtrado)],
    [promedio, promedio],
    linestyle='--',
    linewidth=1.5,
    label=rf'Promedio = {promedio:.4f}'
)

# Banda de desvío
ax.fill_between(
    x_filtrado,
    promedio - desvio,
    promedio + desvio,
    alpha=0.2,
    label=rf'$\sigma$ = {desvio:.4f}'
)

# Línea vertical en X
ax.axvline(
    X,
    linestyle=':',
    linewidth=1.2,
    label=rf'$t = {X}$'
)

# Ejes y formato
ax.set_xlim(min(x), max(x))
ax.set_ylim(0, 1)
ax.set_xlabel(r'Tiempo ($t$)')
ax.set_ylabel(r'Polarización ($v_a$)')
# ax.set_title(r'Indicador de ruido $v_a$ en función del tiempo $t$')

ax.grid(True)
ax.legend()
fig.tight_layout()

# Guardar como PNG
fig.savefig(ruta_salida, dpi=300, bbox_inches='tight')
print(f"Gráfico guardado en: {ruta_salida}")

plt.show()