"""
Punto de entrada principal de la aplicación de control remoto
"""

from controller import CarController


def main():
    """Función principal"""
    app = CarController()
    app.run()


if __name__ == "__main__":
    main()
