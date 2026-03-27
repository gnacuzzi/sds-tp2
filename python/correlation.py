import os
import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

# =========================
# Configuración tipográfica
# =========================
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12

# =========================
# Parámetro: nombre de salida
# =========================
if len(sys.argv) != 3:
    print("Uso: python correlation.py <nombre_salida> <leader>")
    sys.exit(1)

nombre_salida = sys.argv[1]
leader = sys.argv[2]

# =========================
# Configuración
# =========================
INPUT_FILE = "output/dynamic_correlation.txt"
STEP_X = 500
STEP_Y = 0.2
X = 200  # desde dónde calcular estadísticas

# =========================
# Lectura de datos
# =========================
t = []
c = []

with open(INPUT_FILE, "r") as f:
    for line in f:
        if line.strip():
            time, value = map(float, line.split())
            t.append(time)
            c.append(value)

t = np.array(t)
c = np.array(c)

if len(t) == 0:
    print(f"El archivo {INPUT_FILE} está vacío o no contiene datos válidos.")
    sys.exit(1)

# =========================
# Filtrado desde X
# =========================
t_filtrado = [ti for ti in t if ti >= X]
c_filtrado = [ci for ti, ci in zip(t, c) if ti >= X]

if len(c_filtrado) == 0:
    print(f"No hay datos para t >= {X}")
    sys.exit(1)

# =========================
# Estadísticas
# =========================
# promedio = np.mean(c_filtrado)
# desvio = np.std(c_filtrado)

# print(f"Para t >= {X}:")
# print(f"Promedio = {promedio}")
# print(f"Desvío estándar = {desvio}")

# =========================
# Crear carpeta de salida
# =========================
if leader == 0:
    dir = f"graphics/sin_lider/correlation"
else:
    dir = f"graphics/leader{leader}/correlation"
os.makedirs(dir, exist_ok=True)

ruta_png = os.path.join(dir, f"{nombre_salida}.png")
# ruta_txt = os.path.join(f"graphics/leader{leader}/correlation", f"{nombre_salida}.txt")

# =========================
# Guardar TXT
# =========================
# with open(ruta_txt, "w") as f:
#     f.write(f"nombre_imagen: {nombre_salida}.png\n")
#     f.write(f"promedio: {promedio}\n")
#     f.write(f"desvio: {desvio}\n")

# print(f"Datos guardados en: {ruta_txt}")

# =========================
# Gráfico
# =========================
fig, ax = plt.subplots(figsize=(10, 6))

# puntos
ax.scatter(
    t,
    c,
    s=10,
    label=r'$C(t)$'
)

# línea de promedio
# ax.plot(
#     [X, max(t_filtrado)],
#     [promedio, promedio],
#     linestyle='--',
#     linewidth=1.5,
#     label=rf'Promedio = {promedio:.4f}'
# )

# banda de desvío
# ax.fill_between(
#     t_filtrado,
#     promedio - desvio,
#     promedio + desvio,
#     alpha=0.2,
#     label=rf'$\sigma$ = {desvio:.4f}'
# )

# línea vertical en X
ax.axvline(
    X,
    linestyle=':',
    linewidth=1.2,
    label=rf'$t = {X}$'
)

# ticks
ax.xaxis.set_major_locator(MultipleLocator(STEP_X))
ax.yaxis.set_major_locator(MultipleLocator(STEP_Y))

# ejes
ax.set_xlim(0, max(t))
ax.set_ylim(-1.05, 1.05)

ax.set_xlabel(r'Tiempo ($t$)')
ax.set_ylabel(r'Correlación $C(t)$')

# ax.grid(False)
# ax.legend()
fig.tight_layout()

# =========================
# Guardar gráfico
# =========================
fig.savefig(ruta_png, dpi=300, bbox_inches='tight')
plt.close(fig)

print(f"Gráfico guardado en: {ruta_png}")