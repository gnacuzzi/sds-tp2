import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

LEADER_DIRS = {
    "0": "sin_lider",
    "1": "leader1",
    "2": "leader2",
}

# =========================
# Configuración tipográfica
# =========================
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 24
plt.rcParams['axes.labelsize'] = 24
plt.rcParams['xtick.labelsize'] = 24
plt.rcParams['ytick.labelsize'] = 24
plt.rcParams['legend.fontsize'] = 18

# =========================
# Parámetros por defecto
# =========================
X = 200
STEP_X = 200

# =========================
# Validación de argumentos
# =========================
if len(sys.argv) < 4:
    print("Uso: python3 python/va_chart.py <ruta_archivo> <leader> <eta>")
    print("Ejemplo: python3 python/va_chart.py output/va_runs/va_ruido_0.5_lider2.txt 2 0.5")
    sys.exit(1)

input_path = sys.argv[1]
leader = sys.argv[2]
eta = sys.argv[3]

if leader not in LEADER_DIRS:
    print(f"Error: leader inválido: {leader}. Debe ser 0, 1 o 2.")
    sys.exit(1)

leader_dir = os.path.join("graphics", LEADER_DIRS[leader])
os.makedirs(leader_dir, exist_ok=True)

nombre_base = os.path.splitext(os.path.basename(input_path))[0]
ruta_salida = os.path.join(leader_dir, f"{nombre_base}.png")
ruta_resumen = os.path.join(leader_dir, f"{nombre_base}_stats.txt")

# =========================
# Validación de archivo
# =========================
if not os.path.exists(input_path):
    print(f"Error: no existe el archivo {input_path}")
    sys.exit(1)

# =========================
# Leer datos
# =========================
x = []
y = []

with open(input_path, "r") as f:
    for line in f:
        if line.strip():
            t, v = map(float, line.split())
            x.append(t)
            y.append(v)

if len(x) == 0:
    print(f"Error: el archivo {input_path} está vacío o no contiene datos válidos.")
    sys.exit(1)

x = np.array(x)
y = np.array(y)

# =========================
# Filtrado para estadísticas
# =========================
x_filtrado = x[x >= X]
y_filtrado = y[x >= X]

if len(y_filtrado) == 0:
    print(f"Advertencia: no hay datos para t >= {X} en {input_path}.")
    promedio = np.mean(y)
    desvio = np.std(y)
else:
    promedio = np.mean(y_filtrado)
    desvio = np.std(y_filtrado)

print(f"Archivo: {input_path}")
print(f"  Leader = {leader}")
print(f"  Eta = {eta}")
print(f"  Para t >= {X}:")
print(f"  Promedio = {promedio}")
print(f"  Desvío estándar = {desvio}")

with open(ruta_resumen, "w") as f:
    f.write(f"leader {leader}\n")
    f.write(f"eta {eta}\n")
    f.write(f"x_desde {X}\n")
    f.write(f"promedio {promedio}\n")
    f.write(f"desvio {desvio}\n")

# =========================
# Figura
# =========================
fig, ax = plt.subplots(figsize=(10, 6))

# Curva principal
ax.plot(
    x,
    y,
    linestyle='-',
    linewidth=1.5,
    marker='o',
    markersize=3,
    label=rf'$\eta = {eta}$'
)

# Línea vertical en X
if X != 0:
    ax.axvline(
        X,
        linestyle=':',
        linewidth=2.5,
        color='red'
    )

# =========================
# Formato del gráfico
# =========================
ax.set_xlim(0, np.max(x))
ax.set_ylim(0, 1)
ax.xaxis.set_major_locator(MultipleLocator(STEP_X))

ax.set_xlabel(r'Tiempo ($t$)')
ax.set_ylabel(r'Polarización ($v_a$)')

ax.grid(False)
ax.legend(loc='upper right', bbox_to_anchor=(1.01, 0.75))
fig.tight_layout()

# =========================
# Guardar
# =========================
fig.savefig(ruta_salida, dpi=300, bbox_inches='tight')
print(f"Gráfico guardado en: {ruta_salida}")
print(f"Resumen guardado en: {ruta_resumen}")

plt.close(fig)