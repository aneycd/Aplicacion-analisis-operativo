"""Rutas adicionales de la aplicación.

Endpoints:
  - GET /health : estado de la aplicación (JSON)
"""

from flask import jsonify

from app.controllers import main_bp


@main_bp.route("/health")
def health_check():
    """Endpoint de salud de la aplicación."""
    return jsonify(
        {
            "status": "ok",
            "app": "analisis-operativo-servicio-al-cliente",
        }
    )
