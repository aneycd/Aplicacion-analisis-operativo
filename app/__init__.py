"""
Factory de la aplicación Flask.
Siguiendo el patrón MVC: app/__init__.py crea la app, registra blueprints
y carga la configuración desde .env.
"""

import os
from datetime import timedelta
from flask import Flask


def create_app():
    """Crea y configura la aplicación Flask."""
    # Importar routes ANTES de crear la app para que sus rutas
    # se agreguen a main_bp antes del registro
    import app.controllers.routes  # noqa: F401

    flask_app = Flask(__name__)

    # Cargar variables de entorno desde .env
    from dotenv import load_dotenv
    load_dotenv()

    # Verificar que las variables de entorno requeridas existan
    _verificar_variables_entorno()

    flask_app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY"),
        IA_API_KEY=os.environ.get("IA_API_KEY", ""),
        APP_USUARIO=os.environ.get("APP_USUARIO"),
        APP_CLAVE=os.environ.get("APP_CLAVE"),
    )

    # Configurar sesión: expira a las 8 horas
    flask_app.permanent_session_lifetime = timedelta(hours=8)

    # Registrar blueprints de controladores
    from app.controllers import main_bp
    flask_app.register_blueprint(main_bp)

    # Registrar blueprint de exportación
    from app.controllers.export import export_bp
    flask_app.register_blueprint(export_bp)

    return flask_app


def _verificar_variables_entorno():
    """Verifica que las variables de entorno requeridas existan.
    Si falta alguna, imprime un mensaje en consola y la app no permite acceso."""
    requeridas = ["APP_USUARIO", "APP_CLAVE", "SECRET_KEY"]
    faltantes = [v for v in requeridas if not os.environ.get(v)]
    if faltantes:
        nombres = ", ".join(faltantes)
        print(f"\n{'='*60}")
        print(f"Faltan variables de entorno: {nombres}")
        print(f"Configúralas en .env (local) o en Environment (Render).")
        print(f"{'='*60}\n")
