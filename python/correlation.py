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
INPUT_FILE = "output/dynamic_correlation.txt"
OUTPUT_FILE = "graphics/correlation.png"
STEP_X = 500
STEP_Y = 0.2

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
    c,
    s=10,
    label=r'$C(t)$'
)

# Ticks de ejes
ax.xaxis.set_major_locator(MultipleLocator(STEP_X))
ax.yaxis.set_major_locator(MultipleLocator(STEP_Y))

# Ejes y formato
ax.set_xlim(0, max(t))
ax.set_ylim(-1.05, 1.05)

ax.set_xlabel(r'Tiempo ($t$)')
ax.set_ylabel(r'Correlación $C(t)$')
# ax.set_title(r'Correlación líder-sistema en función del tiempo $t$')

ax.grid(True)
ax.legend()
fig.tight_layout()

# =========================
# Guardar gráfico
# =========================
fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
plt.close(fig)

print(f"Gráfico guardado en: {OUTPUT_FILE}")