from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6 import uic

class LoginView(QDialog):
    def __init__(self):
        super().__init__()
        # Si tienes un archivo .ui separado para el login (ej: Login.ui), lo cargas aquí:
        # uic.loadUi("Login.ui", self)
        pass

    def obtener_credenciales(self):
        """Devuelve lo que el usuario haya escrito en los inputs"""
        # Reemplaza 'input_usuario' e 'input_password' por los nombres reales de tus QLineEdit
        usuario = self.input_usuario.text() if hasattr(self, "input_usuario") else ""
        password = self.input_password.text() if hasattr(self, "input_password") else ""
        return usuario, password

    def mostrar_error(self, mensaje):
        QMessageBox.warning(self, "Error de autenticación", mensaje)