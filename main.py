from src.ui.main_window import iniciar_aplicacion
from src.repositories.database import crear_base_datos


def main():
    crear_base_datos()
    iniciar_aplicacion()


if __name__ == "__main__":
    main()