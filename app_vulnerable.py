import os
import sqlite3
from pathlib import Path

from flask import Flask, redirect, render_template_string, request

app = Flask(__name__)
BASE_DATOS = Path(__file__).with_name("base_datos.db")
MODO = os.environ.get("MODO_APP", "vulnerable").lower()

if MODO not in {"vulnerable", "seguro"}:
    raise ValueError("MODO_APP debe ser vulnerable o seguro.")


def preparar_base():
    conexion = sqlite3.connect(BASE_DATOS)
    try:
        with conexion:
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    usuario TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    rol TEXT NOT NULL,
                    email TEXT NOT NULL
                )
            """)
            conexion.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    nombre TEXT PRIMARY KEY,
                    categoria TEXT NOT NULL,
                    precio REAL NOT NULL
                )
            """)
            conexion.executemany(
                "INSERT OR IGNORE INTO usuarios VALUES (?, ?, ?, ?)",
                [
                    ("admin", "DemoAdmin2026!", "administrador",
                     "admin@indicorp.example"),
                    ("jlopez", "DemoVentas2026!", "vendedor",
                     "jlopez@indicorp.example"),
                    ("mtorres", "DemoAuditor2026!", "auditor",
                     "mtorres@indicorp.example"),
                ],
            )
            conexion.executemany(
                "INSERT OR IGNORE INTO productos VALUES (?, ?, ?)",
                [
                    ("Laptop HP ProBook", "Computo", 850.00),
                    ("Monitor LG 24", "Computo", 145.00),
                    ("Mouse inalambrico", "Accesorios", 18.50),
                    ("Teclado mecanico", "Accesorios", 42.00),
                    ("Disco SSD 1TB", "Almacenamiento", 78.00),
                ],
            )
    finally:
        conexion.close()


PAGINA = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>INDICORP - Laboratorio SQL</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #edf1f7;
            color: #203247;
            margin: 0;
        }
        header {
            background: #123e65;
            color: white;
            padding: 22px;
        }
        .etiqueta {
            background: {{ '#a82626' if modo == 'vulnerable' else '#176b40' }};
            padding: 6px 12px;
            border-radius: 6px;
            margin-left: 15px;
            display: inline-block;
        }
        main {
            background: white;
            max-width: 850px;
            margin: 35px auto;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 5px 20px #00000015;
        }
        nav a {
            display: inline-block;
            color: #123e65;
            margin-right: 25px;
            margin-bottom: 15px;
            font-weight: bold;
        }
        label { display: block; margin: 15px 0 6px; }
        input {
            box-sizing: border-box;
            width: 100%;
            padding: 12px;
            border: 1px solid #bbc6d4;
            border-radius: 6px;
        }
        button {
            background: #123e65;
            color: white;
            padding: 12px 22px;
            border: 0;
            border-radius: 6px;
            margin-top: 18px;
            cursor: pointer;
        }
        .aviso {
            background: #fff4d6;
            padding: 12px;
            border-radius: 6px;
        }
        .resultado {
            background: {{ '#def7e7' if exito else '#fde5e5' }};
            padding: 15px;
            margin-top: 20px;
            border-radius: 6px;
        }
        pre {
            background: #101c2a;
            color: #dceaf7;
            padding: 15px;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            border-radius: 6px;
        }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td {
            text-align: left;
            border: 1px solid #d7dfe9;
            padding: 10px;
        }
        th { background: #edf1f7; }
        footer { text-align: center; padding: 20px; color: #596779; }
    </style>
</head>
<body>
    <header>
        INDICORP S.A. | Portal de laboratorio
        <span class="etiqueta">
            {{ 'VULNERABLE' if modo == 'vulnerable'
               else 'CONSULTAS PARAMETRIZADAS' }}
        </span>
    </header>
    <main>
        <nav>
            <a href="/login">Iniciar sesión</a>
            <a href="/buscar">Buscar productos</a>
        </nav>

        <p class="aviso">
            Laboratorio local con datos ficticios.
            No ingresar contraseñas ni información personal real.
        </p>

        {% if seccion == 'login' %}
            <h1>Iniciar sesión</h1>
            <form method="post">
                <label for="usuario">Usuario</label>
                <input id="usuario" name="usuario" required
                       autocomplete="off">
                <label for="password">Contraseña de demostración</label>
                <input id="password" name="password" type="password"
                       required autocomplete="off">
                <button type="submit">Ingresar</button>
            </form>
        {% else %}
            <h1>Buscar productos</h1>
            <form method="get">
                <label for="q">Nombre del producto</label>
                <input id="q" name="q" value="{{ termino }}"
                       placeholder="Por ejemplo: Laptop">
                <button type="submit">Buscar</button>
            </form>
        {% endif %}

        {% if mensaje %}
            <div class="resultado">{{ mensaje }}</div>
        {% endif %}

        {% if filas %}
            <table>
                <thead>
                    <tr>
                        <th>Columna 1</th>
                        <th>Columna 2</th>
                        <th>Columna 3</th>
                    </tr>
                </thead>
                <tbody>
                    {% for fila in filas %}
                        <tr>
                            {% for valor in fila %}
                                <td>{{ valor }}</td>
                            {% endfor %}
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        {% endif %}

        {% if consulta %}
            <h3>Consulta del laboratorio</h3>
            <pre>{{ consulta }}</pre>
            {% if modo == 'seguro' %}
                <p>Los valores se enviaron como parámetros separados.</p>
            {% endif %}
        {% endif %}
    </main>
    <footer>
        Seguridad Informática | Demostración académica local
    </footer>
</body>
</html>
"""


@app.route("/")
def inicio():
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    mensaje = ""
    consulta = ""
    exito = False

    if request.method == "POST":
        usuario = request.form.get("usuario", "")
        password = request.form.get("password", "")
        conexion = sqlite3.connect(BASE_DATOS)

        try:
            if MODO == "seguro":
                consulta = (
                    "SELECT usuario, rol, email FROM usuarios "
                    "WHERE usuario = ? AND password = ?"
                )
                fila = conexion.execute(
                    consulta, (usuario, password)
                ).fetchone()
            else:
                # Inseguro deliberadamente: solo para este laboratorio.
                consulta = (
                    "SELECT usuario, rol, email FROM usuarios "
                    "WHERE usuario = '" + usuario
                    + "' AND password = '" + password + "'"
                )
                fila = conexion.execute(consulta).fetchone()

            if fila:
                exito = True
                mensaje = (
                    f"Acceso concedido. Usuario: {fila[0]} | "
                    f"Rol: {fila[1]}"
                )
            else:
                mensaje = "Acceso denegado. Usuario o contraseña incorrectos."
        except sqlite3.Error:
            mensaje = "La consulta no pudo procesarse."
        finally:
            conexion.close()

    return render_template_string(
        PAGINA, modo=MODO, seccion="login",
        mensaje=mensaje, consulta=consulta, exito=exito,
        filas=[], termino=""
    )


@app.route("/buscar")
def buscar():
    termino = request.args.get("q", "")
    mensaje = ""
    consulta = ""
    filas = []
    exito = False

    if "q" in request.args:
        conexion = sqlite3.connect(BASE_DATOS)
        try:
            if MODO == "seguro":
                consulta = (
                    "SELECT nombre, categoria, precio FROM productos "
                    "WHERE nombre LIKE ?"
                )
                filas = conexion.execute(
                    consulta, ("%" + termino + "%",)
                ).fetchall()
            else:
                # Inseguro deliberadamente: solo para este laboratorio.
                consulta = (
                    "SELECT nombre, categoria, precio FROM productos "
                    "WHERE nombre LIKE '%" + termino + "%'"
                )
                filas = conexion.execute(consulta).fetchall()

            exito = True
            mensaje = f"{len(filas)} registro(s) encontrado(s)."
        except sqlite3.Error:
            mensaje = "La consulta no pudo procesarse."
        finally:
            conexion.close()

    return render_template_string(
        PAGINA, modo=MODO, seccion="buscar",
        mensaje=mensaje, consulta=consulta, exito=exito,
        filas=filas, termino=termino
    )


if __name__ == "__main__":
    preparar_base()
    print(f"Laboratorio INDICORP | Modo: {MODO}")
    print("Solo datos ficticios. No usar en produccion.")
    app.run(host="127.0.0.1", port=5000, debug=False)