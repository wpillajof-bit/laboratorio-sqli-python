import argparse
import csv
import socket
from datetime import datetime
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Escaner TCP del laboratorio local."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument(
        "--puertos",
        default="22,80,443,3306,5000,8080",
    )
    args = parser.parse_args()

    if args.host != "127.0.0.1":
        parser.error("Este laboratorio solo permite 127.0.0.1.")

    try:
        puertos = sorted(set(
            int(valor.strip())
            for valor in args.puertos.split(",")
        ))
        if not puertos or any(p < 1 or p > 65535 for p in puertos):
            raise ValueError
    except ValueError:
        parser.error("Indica puertos entre 1 y 65535 separados por comas.")

    print("=" * 60)
    print("ESCANER BASICO TCP - LABORATORIO INDICORP")
    print(f"Objetivo: {args.host}")
    print("Se comprueba conexion TCP, no identidad del servicio.")
    print("=" * 60)

    resultados = []

    for puerto in puertos:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                codigo = sock.connect_ex((args.host, puerto))

            estado = "ABIERTO" if codigo == 0 else "SIN CONEXION"
            detalle = f"codigo={codigo}"
        except OSError as error:
            estado = "ERROR"
            detalle = str(error)

        print(f"[{estado}] puerto {puerto}")
        resultados.append({
            "host": args.host,
            "puerto": puerto,
            "estado": estado,
            "detalle": detalle,
        })

    abiertos = sum(r["estado"] == "ABIERTO" for r in resultados)
    print(f"\nPuertos abiertos detectados: {abiertos}")
    print("Puerto abierto no significa vulnerabilidad confirmada.")
    print("SIN CONEXION no distingue cerrado de filtrado.")

    carpeta = Path(__file__).parent / "evidencias"
    carpeta.mkdir(exist_ok=True)
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo = carpeta / f"escaneo_{fecha}.csv"

    with archivo.open("w", newline="", encoding="utf-8-sig") as salida:
        escritor = csv.DictWriter(
            salida,
            fieldnames=["host", "puerto", "estado", "detalle"],
        )
        escritor.writeheader()
        escritor.writerows(resultados)

    print(f"Resultados guardados en: {archivo}")


if __name__ == "__main__":
    main()