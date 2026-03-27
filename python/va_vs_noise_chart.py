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

GRAPHICS_DIR = "graphics"
OUTPUT_FILE = os.path.join(GRAPHICS_DIR, "va_vs_ruido_toma_1.png")

# Regex para aceptar nombres tipo:
# ruido_4.2_toma_1.png
# ruido_0.0_toma_1.png
PATRON_IMAGEN = re.compile(r"^ruido_(\d+(?:\.\d+)?)_toma_1\.png$")


def parse_txt_file(filepath):
    """
    Lee un txt con formato:
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
        "archivo_txt": filepath,
        "nombre_imagen": nombre_imagen,
    }


def main():
    if not os.path.isdir(GRAPHICS_DIR):
        print(f"No existe la carpeta: {GRAPHICS_DIR}")
        sys.exit(1)

    datos = []

    for filename in os.listdir(GRAPHICS_DIR):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(GRAPHICS_DIR, filename)
        resultado = parse_txt_file(filepath)

        # Solo toma archivos válidos y solo toma_1
        if resultado is not None:
            datos.append(resultado)

    if not datos:
        print("No se encontraron archivos .txt válidos de toma_1 en graphics/")
        sys.exit(1)

    # Ordenar por ruido
    datos.sort(key=lambda d: d["ruido"])

    ruidos = [d["ruido"] for d in datos]
    promedios = [d["promedio"] for d in datos]
    desvios = [d["desvio"] for d in datos]

    # =========================
    # Gráfico
    # =========================
    fig, ax = plt.subplots(figsize=(10, 6))

    # Líneas cada 0.25 en eje X
    ax.xaxis.set_major_locator(MultipleLocator(0.25))

    ax.errorbar(
        ruidos,
        promedios,
        yerr=desvios,
        fmt='o',
        markersize=5,
        capsize=4,
        linestyle='-',
        zorder=3,
    )

    ax.set_xlim(0, 5)
    ax.set_ylim(0, 1)

    ax.set_xlabel(r'Ruido ($\eta$)')
    ax.set_ylabel(r'Polarización promedio ($v_a$)')
    # ax.set_title(r'Polarización promedio en función del ruido')

    fig.tight_layout()

    fig.savefig(OUTPUT_FILE, dpi=300, bbox_inches='tight')
    print(f"Gráfico guardado en: {OUTPUT_FILE}")

    # plt.show()


if __name__ == "__main__":
    main()