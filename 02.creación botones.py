import sys
import json
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout
from PyQt6.uic import loadUi


class TPVApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # 1. Cargar la interfaz limpia desde Qt Designer
        loadUi("Diseño.ui", self)  # <-- Pon aquí el nombre exacto de tu archivo .ui

        # 2. Cargar los datos del JSON
        self.datos_tpv = self.cargar_json()

        # 3. Asegurar y capturar los Layouts donde se pintarán los botones
        if not self.frame_PRODUCTOS.layout():
            self.layout_categorias = QGridLayout(self.frame_PRODUCTOS)
        else:
            self.layout_categorias = self.frame_PRODUCTOS.layout()

        # Capturamos el layout de la página activa del stackedWidget
        if not self.stackedWidget.currentWidget().layout():
            self.layout_productos = QGridLayout(self.stackedWidget.currentWidget())
        else:
            self.layout_productos = self.stackedWidget.currentWidget().layout()

        # 4. ¡Arrancar la generación dinámica de categorías!
        self.dibujar_categorias()

    def cargar_json(self):
        with open("BASEDATOS.json", "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    def dibujar_categorias(self):
        """Genera los botones de categorías con imágenes en la parte superior derecha"""
        columnas_maximas = 4
        fila = 0
        columna = 0

        for cat in self.datos_tpv["categorias"]:
            boton_cat = QPushButton()
            boton_cat.setMinimumSize(110, 75)  # Puedes ajustar el tamaño para que cuadren bien

            # Construimos la ruta usando el ID de la categoría (ej: imagenes/cat_refrescos.jpg)
            ruta_imagen = f"imagenes/{cat['id']}.jpg"

            # Si la imagen existe en la carpeta, se la ponemos de fondo
            if os.path.exists(ruta_imagen):
                boton_cat.setStyleSheet(f"""
                            QPushButton {{
                                border-image: url({ruta_imagen});
                                border-radius: 5px;
                                border: 1px solid #333333;
                            }}
                            QPushButton:pressed {{
                                border: 2px solid #00FF00;
                            }}
                        """)
            else:
                # Si falta alguna imagen, dejamos el botón azul con texto para que no se quede invisible
                boton_cat.setText(cat["nombre"])
                boton_cat.setStyleSheet("""
                            QPushButton {
                                background-color: #34495e;
                                color: white;
                                font-weight: bold;
                                border-radius: 5px;
                            }
                            QPushButton:hover { background-color: #2c3e50; }
                        """)

            # Al pulsar la categoría, se cargan sus productos correspondientes
            boton_cat.clicked.connect(lambda checked, c_id=cat["id"]: self.dibujar_productos(c_id))

            # Añadir al panel superior
            self.layout_categorias.addWidget(boton_cat, fila, columna)

            columna += 1
            if columna >= columnas_maximas:
                columna = 0
                fila += 1

    def limpiar_productos(self):
        while self.layout_productos.count():
            item = self.layout_productos.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def dibujar_productos(self, categoria_id):
        """Genera los botones con imágenes en el panel inferior al pulsar una categoría"""
        self.limpiar_productos()

        # Filtrar productos de la categoría seleccionada
        productos_filtrados = [p for p in self.datos_tpv["productos"] if p["categoria_id"] == categoria_id]

        columnas_maximas = 4
        fila, columna = 0, 0

        for prod in productos_filtrados:
            boton_prod = QPushButton()
            boton_prod.setMinimumSize(120, 90)

            # Ruta de la imagen asociada al ID
            ruta_imagen = f"imagenes/{prod['id']}.jpg"

            # Si la imagen no existe, ponemos un color gris con el nombre para que no falle
            if os.path.exists(ruta_imagen):
                boton_prod.setStyleSheet(f"""
                    QPushButton {{
                        border-image: url({ruta_imagen});
                        border-radius: 6px;
                    }}
                    QPushButton:pressed {{ border: 3px solid #2ecc71; }}
                """)
            else:
                boton_prod.setText(f"{prod['nombre']}\n{prod['precio']:.2f}€")
                boton_prod.setStyleSheet("background-color: #7f8c8d; color: white; border-radius: 6px;")

            # Acción al pulsar el producto
            boton_prod.clicked.connect(lambda checked, p=prod: self.producto_pulsado(p))

            self.layout_productos.addWidget(boton_prod, fila, columna)

            columna += 1
            if columna >= columnas_maximas:
                columna = 0
                fila += 1

    def producto_pulsado(self, producto):
        print(f"Añadido al ticket: {producto['nombre']} - {producto['precio']}€")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = TPVApp()
    ventana.show()
    sys.exit(app.exec())