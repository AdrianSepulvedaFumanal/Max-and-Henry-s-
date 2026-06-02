import sys
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout,
                             QHBoxLayout, QLabel, QComboBox,
                             QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
# Importamos la ventana del TPV desde tu script principal
from Cuenta import TPVApp


class LoginVentana(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔐 Acceso al Sistema TPV")
        self.resize(350, 220)
        # Estilo oscuro integrado a juego con tu barra de productos
        self.setStyleSheet("""
            QDialog { background-color: #1a1a1a; color: white; font-family: Arial; }
            QLabel { color: #bdc3c7; font-size: 13px; font-weight: bold; }
            QComboBox { background-color: #2c3e50; color: white; padding: 6px; border-radius: 4px; border: 1px solid #34495e; font-size: 13px; }
            QLineEdit { background-color: #242424; color: white; padding: 6px; border-radius: 4px; border: 1px solid #333333; font-size: 13px; }
            QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 8px; border-radius: 5px; border: none; font-size: 13px; }
            QPushButton:hover { background-color: #2ecc71; }
            QPushButton#btn_cancelar { background-color: #7f8c8d; }
            QPushButton#btn_cancelar:hover { background-color: #95a5a6; }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Selector de Usuarios
        layout.addWidget(QLabel("Seleccione Usuario / Empleado:"))
        self.combo_usuarios = QComboBox()
        self.combo_usuarios.addItems([
            "Camarero 1",
            "Camarero 2",
            "Camarero 3",
            "Camarero 4",
            "Camarero 5",
            "Administrador"
        ])
        layout.addWidget(self.combo_usuarios)

        # Campo de Contraseña
        self.lbl_pass = QLabel("Contraseña de Administrador:")
        layout.addWidget(self.lbl_pass)
        self.input_pass = QLineEdit()
        self.input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pass.setPlaceholderText("Introduce el PIN de seguridad")
        layout.addWidget(self.input_pass)

        # Por defecto, ocultamos el campo de contraseña ya que inicia en Camarero 1
        self.lbl_pass.setVisible(False)
        self.input_pass.setVisible(False)

        # Conectar el selector para que pida contraseña SOLO cuando elijas "Administrador"
        self.combo_usuarios.currentIndexChanged.connect(self.controlar_visibilidad_password)

        # Botonera inferior
        layout_botones = QHBoxLayout()
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btn_cancelar")
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_entrar = QPushButton("Entrar al TPV")
        self.btn_entrar.clicked.connect(self.validar_credenciales)

        layout_botones.addWidget(self.btn_cancelar)
        layout_botones.addWidget(self.btn_entrar)
        layout.addLayout(layout_botones)

        self.rol_elegido = None

    def controlar_visibilidad_password(self):
        es_admin = (self.combo_usuarios.currentText() == "Administrador")
        self.lbl_pass.setVisible(es_admin)
        self.input_pass.setVisible(es_admin)
        if es_admin:
            self.input_pass.setFocus()
        else:
            self.input_pass.clear()

    def validar_credenciales(self):
        usuario = self.combo_usuarios.currentText()

        if usuario == "Administrador":
            # Validación de la clave solicitada (1234)
            if self.input_pass.text() == "1234":
                self.rol_elegido = "admin"
                self.accept()
            else:
                QMessageBox.critical(self, "Acceso Denegado", "❌ Contraseña incorrecta. Inténtalo de nuevo.")
                self.input_pass.clear()
                self.input_pass.setFocus()
        else:
            # Los camareros entran directo sin clave
            self.rol_elegido = "camarero"
            self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 1. Ejecutamos la pantalla de Login primero
    ventana_login = LoginVentana()
    if ventana_login.exec() == QDialog.DialogCode.Accepted:
        # 2. Si las credenciales son válidas, abrimos el TPV pasándole el rol correspondiente
        ventana_tpv = TPVApp(
            rol=ventana_login.role_elegido if hasattr(ventana_login, 'role_elegido') else ventana_login.rol_elegido)
        ventana_tpv.show()
        sys.exit(app.exec())