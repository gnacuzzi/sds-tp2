import os
import re
import sys
import matplotlib.pyplot as plt
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
# Carpetas de entrada
# =========================
BASE_DIR = "graphics"

CARPETAS = {
    "Sin líder": os.path.join(BASE_DIR, "sin_lider"),
    "Líder fijo": os.path.join(BASE_DIR, "leader1"),
    "Líder circular": os.path.join(BASE_DIR, "leader2"),
}

OUTPUT_FILE = os.path.join(BASE_DIR, "comparacion_lideres.png")

PATRON_IMAGEN = re.compile(r"^ruido_(\d+(?:\.\d+)?)_toma_1\.png$")


def parse_txt_file(filepath):
    """
    Lee archivos con formato:
    leader 1
    eta 0
    x_desde 200
    promedio 0.996608791227096
    desvio 0.004390879999646369
    """

    ruido = None
    promedio = None
    desvio = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith("eta"):
                # ejemplo: "eta 0"
                ruido = float(line.split()[1])

            elif line.startswith("promedio"):
                promedio = float(line.split()[1])

            elif line.startswith("desvio"):
                desvio = float(line.split()[1])

    if ruido is None or promedio is None or desvio is None:
        return None

    return {
        "ruido": ruido,
        "promedio": promedio,
        "desvio": desvio,
    }


def read_folder(folder_path):
    """
    Lee todos los .txt válidos de una carpeta.
    """
    if not os.path.isdir(folder_path):
        print(f"Advertencia: no existe la carpeta {folder_path}")
        return []

    datos = []

    for filename in os.listdir(folder_path):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(folder_path, filename)
        parsed = parse_txt_file(filepath)

        if parsed is not None:
            datos.append(parsed)

    datos.sort(key=lambda d: d["ruido"])
    return datos


def main():
    series = {}

    for nombre_serie, carpeta in CARPETAS.items():
        datos = read_folder(carpeta)
        if datos:
            series[nombre_serie] = datos
        else:
            print(f"Advertencia: no se encontraron datos válidos en {carpeta}")

    if not series:
        print("No se encontraron datos para graficar.")
        sys.exit(1)

    fig, ax = plt.subplots(figsize=(10, 6))

    for nombre_serie, datos in series.items():
        ruidos = [d["ruido"] for d in datos]
        promedios = [d["promedio"] for d in datos]
        desvios = [d["desvio"] for d in datos]

        ax.errorbar(
            ruidos,
            promedios,
            yerr=desvios,
            fmt='o',
            markersize=4,
            capsize=3,
            linestyle='-',
            zorder=3,
            label=nombre_serie
        )

    ax.set_xlim(0, 5)
    ax.set_ylim(0, 1.02)

    ax.xaxis.set_major_locator(MultipleLocator(0.25))

    ax.set_xlabel(r'Ruido ($\eta$)')
    ax.set_ylabel(r'Polarización promedio ($v_a$)')
    # ax.set_title(r'Polarización promedio en función del ruido')

    # ax.grid(False, zorder=0)
    ax.legend()
    fig.tight_layout()

    fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    print(f"Gráfico guardado en: {OUTPUT_FILE}")

    # plt.show()


if __name__ == "__main__":
    main()