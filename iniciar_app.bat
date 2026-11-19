@echo off
cd /d "%~dp0"

:: Activar entorno de uv si existe
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

:: Instalar dependencias si no están instaladas
uv sync --frozen 2>nul || uv add flask python-dotenv openpyxl

:: Iniciar la aplicación Flask
set FLASK_APP=wsgi.py
set FLASK_ENV=development
python -m flask run --host=127.0.0.1 --port=5000

:: Abrir el navegador en la URL local
start http://127.0.0.1:5000/
