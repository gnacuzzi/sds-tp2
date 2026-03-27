from math import pi
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import MultipleLocator

# =========================
# Configuración tipográfica
# =========================
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.unicode_minus'] = False

# =========================
# Configuración
# =========================
INPUT_FILE = "output/dynamic_mean_angle.txt"
OUTPUT_FILE = "graphics/mean_angle.png"
STEP_X = 500
STEP_Y = 20

# =========================
# Lectura de datos
# =========================
t = []
theta = []

with open(INPUT_FILE, "r") as f:
    for line in f:
        if line.strip():
            time, value = map(float, line.split())
            t.append(time)
            theta.append(value * 180 / pi)

t = np.array(t)
theta = np.array(theta)

if len(t) == 0:
    print(f"El archivo {INPUT_FILE} está vacío o no contiene datos válidos.")
    exit(1)

# =========================
# Crear carpeta de salida
# =========================
os.makedirs("graphics", exist_ok=True)

# =========================
# Gráfico
# =========================
fig, ax = plt.subplots(figsize=(10, 6))

# Solo puntos, sin línea continua
ax.scatter(
    t,
    theta,
    s=10,
    label=r'$\theta_s(t)$'
)

# Ticks de ejes
ax.xaxis.set_major_locator(MultipleLocator(STEP_X))
ax.yaxis.set_major_locator(MultipleLocator(STEP_Y))

# Ejes y formato
ax.set_xlim(0, max(t))
ax.set_ylim(-180, 180)

ax.set_xlabel(r'Tiempo ($t$)')
ax.set_ylabel(r'Ángulo medio $\theta_s(t)$ [$^\circ$]')

ax.grid(True)
ax.legend()
fig.tight_layout()

# =========================
# Guardar gráfico
# =========================
fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
plt.close(fig)

print(f"Gráfico guardado en: {OUTPUT_FILE}")