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
        QMessageBox.critical(None, "Error de Sistema", "No se encontró el archivo 'Login.py' en la raíz.")
        sys.exit(1)

    # 2. Una vez logueado con éxito, inicializamos los componentes del TPV
    model = DataBaseModel()
    model.rol_actual = rol_usuario  # Inyectamos el rol validado del login en el modelo

    view = MainView()

    # === EL TRUCO DE CORRECCIÓN VISUAL ===
    # Primero mostramos la pantalla para que Qt inicialice todos los contenedores reales en el OS
    view.mostrar_pantalla()

    # Luego instanciamos el presentador, que ahora sí encontrará los layouts listos para pintar
    presenter = MainPresenter(view, model)

    # 3. Iniciamos el bucle principal de eventos de la aplicación gráfica
    sys.exit(app.exec())


if __name__ == "__main__":
    main()