"""
Factory de la aplicación Flask.
Siguiendo el patrón MVC: app/__init__.py crea la app, registra blueprints
y carga la configuración desde .env.
"""

import os
from flask import Flask


def create_app():
    """Crea y configura la aplicación Flask."""
    # Importar routes ANTES de crear la app para que sus rutas
    # se agreguen a main_bp antes del registro
    import app.controllers.routes  # noqa: F401

    flask_app = Flask(__name__)

    # Cargar variables de entorno desde .env
    flask_app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        IA_API_KEY=os.environ.get("IA_API_KEY", ""),
    )

    # Registrar blueprints de controladores
    from app.controllers import main_bp
    flask_app.register_blueprint(main_bp)

    # Registrar blueprint de exportación
    from app.controllers.export import export_bp
    flask_app.register_blueprint(export_bp)

    return flask_app
