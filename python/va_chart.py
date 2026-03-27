import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# =========================
# Configuración tipográfica
# =========================
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 28
plt.rcParams['axes.labelsize'] = 28
plt.rcParams['xtick.labelsize'] = 28
plt.rcParams['ytick.labelsize'] = 28
plt.rcParams['legend.fontsize'] = 20

# =========================
# Configuración de archivos
# =========================
FILES = [
    {
        "path": "output/va_ruido0_lider1.txt",
        "label": r'$\eta = 0$',
        "X": 200,
        "STEP_X": 200,
    },
    {
        "path": "output/va_ruido2_lider1.txt",
        "label": r'$\eta = 2$',
        "X": 200,
        "STEP_X": 200,
    },
    {
        "path": "output/va_ruido4_lider1.txt",
        "label": r'$\eta = 4$',
        "X": 0,
        "STEP_X": 200,
    },
]

# =========================
# Salida
# =========================
os.makedirs("graphics", exist_ok=True)
ruta_salida = os.path.join("graphics", "va_comparado.png")

# =========================
# Figura
# =========================
fig, ax = plt.subplots(figsize=(10, 6))

global_x_min = None
global_x_max = None

# =========================
# Procesar cada archivo
# =========================
for config in FILES:
    path = config["path"]
    label = config["label"]
    X = config["X"]
    STEP_X = config["STEP_X"]

    if not os.path.exists(path):
        print(f"Advertencia: no existe el archivo {path}. Se omite.")
        continue

    x = []
    y = []

    with open(path, "r") as f:
        for line in f:
            if line.strip():
                t, v = map(float, line.split())
                x.append(t)
                y.append(v)

    if len(x) == 0:
        print(f"Advertencia: el archivo {path} está vacío o no contiene datos válidos. Se omite.")
        continue

    x = np.array(x)
    y = np.array(y)

    x_filtrado = x[x >= X]
    y_filtrado = y[x >= X]

    if len(y_filtrado) == 0:
        print(f"Advertencia: no hay datos para t >= {X} en {path}. Se omite.")
        continue

    promedio = np.mean(y_filtrado)
    desvio = np.std(y_filtrado)

    print(f"Archivo: {path}")
    print(f"  Para t >= {X}:")
    print(f"  Promedio = {promedio}")
    print(f"  Desvío estándar = {desvio}")

    # Curva principal
    ax.plot(
        x,
        y,
        linestyle='-',
        linewidth=1.5,
        marker='o',
        markersize=3,
        label=label
    )

    # Promedio comentado
    # ax.plot(
    #     [X, max(x_filtrado)],
    #     [promedio, promedio],
    #     linestyle='--',
    #     linewidth=1.5
    # )

    # Banda de desvío comentada
    # ax.fill_between(
    #     x_filtrado,
    #     promedio - desvio,
    #     promedio + desvio,
    #     alpha=0.2
    # )

    # Línea vertical en X comentada
    if(X != 0):
        ax.axvline(
            X,
            linestyle=':',
            linewidth=2.5,
            color='red'
        )

    if global_x_min is None:
        global_x_min = np.min(x)
        global_x_max = np.max(x)
    else:
        global_x_min = min(global_x_min, np.min(x))
        global_x_max = max(global_x_max, np.max(x))

    # Si querés usar algún STEP_X particular, acá podrías hacerlo.
    # Como hay varios archivos, tomo el menor STEP_X para un eje consistente.
    # Esto evita que cada curva tenga ticks distintos.
    if "global_step_x" not in locals():
        global_step_x = STEP_X
    else:
        global_step_x = min(global_step_x, STEP_X)

# =========================
# Validación final
# =========================
if global_x_min is None or global_x_max is None:
    print("No se pudo graficar ningún archivo válido.")
    exit(1)

# =========================
# Formato del gráfico
# =========================
ax.set_xlim(0, global_x_max)
ax.set_ylim(0, 1)
ax.xaxis.set_major_locator(MultipleLocator(global_step_x))

ax.set_xlabel(r'Tiempo ($t$)')
ax.set_ylabel(r'Polarización ($v_a$)')

ax.grid(False)
ax.legend(loc='upper right')
fig.tight_layout()

# =========================
# Guardar
# =========================
fig.savefig(ruta_salida, dpi=300, bbox_inches='tight')
print(f"Gráfico guardado en: {ruta_salida}")

plt.show()