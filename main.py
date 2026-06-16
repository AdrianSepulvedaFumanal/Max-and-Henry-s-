import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from models.database import DataBaseModel
from views.main_view import MainView
from presenters.main_presenter import MainPresenter


def main():
    app = QApplication(sys.argv)

    # 1. Intentamos abrir la pantalla de Login primero
    try:
        import Login
        dialogo_login = Login.LoginVentana()

        # .exec() pausa la ejecución aquí y espera a que el usuario interactúe
        if not dialogo_login.exec():
            # Si el usuario cierra la ventana de login o le da a Cancelar, salimos del programa
            sys.exit(0)

        # Si el login es correcto, extraemos el rol elegido ("admin", "camarero", etc.)
        rol_usuario = dialogo_login.rol_elegido

    except ModuleNotFoundError:
        # Salvavidas por si el archivo Login no está accesible en la raíz
        QMessageBox.critical(None, "Error de Sistema", "No se encontró el archivo 'Login.py'.")
        sys.exit(1)

    # 2. Una vez logueado con éxito, inicializamos el TPV con el rol correcto
    model = DataBaseModel()
    model.rol_actual = rol_usuario  # Guardamos el rol validado en el modelo

    view = MainView()
    presenter = MainPresenter(view, model)

    # 3. Mostramos el TPV al fin
    view.mostrar_pantalla()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()