"""
Punto de entrada WSGI para despliegue.
Importa la factory create_app y expone la aplicación.
"""

from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run(debug=True)
