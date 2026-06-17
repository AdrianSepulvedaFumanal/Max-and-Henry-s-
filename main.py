import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from models.database import DataBaseModel
from views.main_view import MainView
from views.login_view import LoginVentana
from presenters.main_presenter import MainPresenter


def main():
    app = QApplication(sys.argv)

    # 1. Pantalla de Login
    dialogo_login = LoginVentana()
    if not dialogo_login.exec():
        sys.exit(0)

    rol_usuario = dialogo_login.rol_elegido

    # 2. Inicializar modelo, vista y presentador
    model = DataBaseModel()
    model.rol_actual = rol_usuario

    view = MainView()
    view.mostrar_pantalla()

    presenter = MainPresenter(view, model)

    # 3. Bucle principal
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
