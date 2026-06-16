from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6 import uic


class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        # Carga tu archivo Diseño.ui de la raíz
        uic.loadUi("Diseño.ui", self)

    def mostrar_pantalla(self):
        self.showMaximized()

    def mostrar_alerta(self, titulo, mensaje):
        """Muestra una alerta flotante en pantalla"""
        QMessageBox.information(self, titulo, mensaje)

    def cambiar_pantalla(self, indice):
        """Cambia de vista usando tu stackedWidget (0 para login, 1 para TPV, etc.)"""
        if hasattr(self, "stackedWidget"):
            self.stackedWidget.setCurrentIndex(indice)

    def _limpiar_layout(self, layout):
        """Método auxiliar interno para vaciar cualquier layout de botones"""
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

    def limpiar_panel_mesas(self):
        """Vacía los botones del contenedor de mesas usando tu frame_MESAS"""
        if hasattr(self, "frame_MESAS") and self.frame_MESAS.layout():
            self._limpiar_layout(self.frame_MESAS.layout())

    def limpiar_panel_productos(self):
        """Vacía los botones del contenedor de productos usando tu frame_PRODUCTOS"""
        if hasattr(self, "frame_PRODUCTOS") and self.frame_PRODUCTOS.layout():
            self._limpiar_layout(self.frame_PRODUCTOS.layout())