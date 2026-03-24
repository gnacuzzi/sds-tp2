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

# =========================
# Carpetas de entrada
# =========================
BASE_DIR = "graphics"

CARPETAS = {
    "Sin líder": os.path.join(BASE_DIR, "sin_lider"),
    "Líder 1": os.path.join(BASE_DIR, "leader1"),
    "Líder 2": os.path.join(BASE_DIR, "leader2"),
}

OUTPUT_FILE = os.path.join(BASE_DIR, "comparacion_lideres.png")

PATRON_IMAGEN = re.compile(r"^ruido_(\d+(?:\.\d+)?)_toma_1\.png$")


def parse_txt_file(filepath):
    """
    Lee archivos con formato:
    nombre_imagen: ruido_4.2_toma_1.png
    promedio: 0.157046405330372
    desvio: 0.069702811680646
    """
    nombre_imagen = None
    promedio = None
    desvio = None

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith("nombre_imagen:"):
                nombre_imagen = line.split(":", 1)[1].strip()

            elif line.startswith("promedio:"):
                promedio = float(line.split(":", 1)[1].strip())

            elif line.startswith("desvio:"):
                desvio = float(line.split(":", 1)[1].strip())

    if nombre_imagen is None or promedio is None or desvio is None:
        return None

    match = PATRON_IMAGEN.match(nombre_imagen)
    if not match:
        return None

    ruido = float(match.group(1))

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
            linestyle='none',
            zorder=3,
            label=nombre_serie
        )

    ax.set_xlim(0, 5)
    ax.set_ylim(0, 1.02)

    ax.xaxis.set_major_locator(MultipleLocator(0.25))

    ax.set_xlabel(r'Ruido ($\eta$)')
    ax.set_ylabel(r'Polarización promedio ($v_a$)')
    # ax.set_title(r'Polarización promedio en función del ruido')

    ax.grid(True, zorder=0)
    ax.legend()
    fig.tight_layout()

    fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    print(f"Gráfico guardado en: {OUTPUT_FILE}")

    plt.show()


if __name__ == "__main__":
    main()