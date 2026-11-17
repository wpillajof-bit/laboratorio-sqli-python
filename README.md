# laboratorio-sqli-python
Laboratorio académico local de SQL Injection con Python, Flask y SQLite: pruebas controladas, consultas parametrizadas y escaneo TCP local.
# Laboratorio de SQL Injection con Python

Proyecto académico local de Seguridad Informática desarrollado con Python, Flask y SQLite.

El laboratorio compara una aplicación deliberadamente vulnerable a SQL Injection con una versión que utiliza consultas parametrizadas. Incluye pruebas automatizadas y un escáner TCP limitado al equipo local.

## Uso autorizado

Utilizar únicamente en el laboratorio propio y con datos ficticios.

No ejecutar pruebas contra sistemas ajenos ni publicar esta aplicación como un servicio accesible desde Internet.

El modo parametrizado demuestra una mitigación de SQL Injection; no convierte esta aplicación académica en un sistema listo para producción.

## Archivos principales

- app_vulnerable.py: aplicación Flask con inicio de sesión, búsqueda de productos y dos modos de consulta.
- ataque_sql_i.py: pruebas automatizadas contra la aplicación local.
- escaneo_red.py: comprobación de conexiones TCP en 127.0.0.1.
- requirements.txt: dependencias externas.
- .gitignore: reglas para excluir archivos locales del control de versiones.

## Entorno utilizado

- Windows 11.
- Python 3.13.3.
- Flask.
- requests.
- SQLite mediante el módulo sqlite3 de Python.

## Instalación en Windows

Descargar el repositorio y abrir una terminal de PowerShell dentro de la carpeta del proyecto.

Crear un entorno virtual:

```powershell
py -m venv .venv
```

Instalar las dependencias:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Los comandos siguientes utilizan directamente el Python del entorno virtual, sin necesidad de activarlo.

## Ejecutar el modo vulnerable

En PowerShell:

```powershell
$env:MODO_APP = "vulnerable"
.\.venv\Scripts\python.exe app_vulnerable.py
```

Abrir en el navegador:

http://127.0.0.1:5000

La aplicación prepara una base de datos local con registros ficticios.

Mantener esta terminal abierta mientras se realizan las pruebas.

## Ejecutar las pruebas automatizadas

Abrir una segunda terminal de PowerShell en la misma carpeta y ejecutar:

```powershell
.\.venv\Scripts\python.exe ataque_sql_i.py
```

El script realiza pruebas de evasión del inicio de sesión, extracción mediante UNION y controles de funcionamiento normal.

## Cambiar al modo parametrizado

En la terminal donde se ejecuta Flask, detener la aplicación con Ctrl+C.

Después ejecutar:

```powershell
$env:MODO_APP = "seguro"
.\.venv\Scripts\python.exe app_vulnerable.py
```

Repetir las pruebas desde la segunda terminal:

```powershell
.\.venv\Scripts\python.exe ataque_sql_i.py
```

En este modo, la aplicación envía los valores de entrada como parámetros separados de la consulta SQL.

## Ejecutar el escáner TCP local

Con la aplicación en ejecución, abrir otra terminal en la carpeta del proyecto:

```powershell
.\.venv\Scripts\python.exe escaneo_red.py
```

El escáner se limita a 127.0.0.1 y comprueba por defecto los puertos 22, 80, 443, 3306, 5000 y 8080.

Una conexión TCP exitosa indica un puerto abierto, pero no identifica por sí sola el servicio ni demuestra una vulnerabilidad.

## Resultados reportados de la práctica

Los siguientes resultados corresponden a las ejecuciones locales reportadas por el autor; no son una garantía de resultados para otros equipos.

| Indicador | Modo vulnerable | Modo parametrizado |
|---|---:|---:|
| Pruebas de ataque exitosas | 6 de 6 | 0 de 6 |
| Controles correctos | 3 de 3 | 3 de 3 |

En la demostración vulnerable, una búsqueda UNION mostró ocho registros: cinco productos y tres usuarios ficticios.

En una ejecución del escáner se reportaron abiertos los puertos 3306 y 5000. Esto no confirma por sí solo qué servicios los utilizan.

## Evidencias

Los clips de demostración se conservan por separado; no están incluidos en este repositorio.

El escáner genera resultados CSV dentro de una carpeta local llamada evidencias.

## Limitaciones de seguridad

- La aplicación contiene vulnerabilidades intencionales para su estudio.
- Las credenciales de demostración son ficticias y no deben reutilizarse.
- El almacenamiento de contraseñas de este laboratorio no representa una implementación adecuada para producción.
- Las consultas parametrizadas no sustituyen otras medidas de seguridad.
- No se deben subir credenciales personales, el entorno .venv ni información privada al repositorio.

## Uso de inteligencia artificial

Se utilizó inteligencia artificial como apoyo en la elaboración y revisión de código, explicaciones y materiales del laboratorio.

La ejecución de las pruebas locales y la preparación de las evidencias estuvieron a cargo del autor.
