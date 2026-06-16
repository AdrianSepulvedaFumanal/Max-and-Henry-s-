import os
from PyQt6.QtWidgets import QPushButton, QGridLayout
from models.database import DataBaseModel
from views.main_view import MainView

class MainPresenter:
    def __init__(self, view: MainView, model: DataBaseModel):
        self.view = view
        self.model = model

        # Asegurar y capturar los Layouts desde la Vista donde se pintarán los botones
        if not self.view.frame_PRODUCTOS.layout():
            self.layout_categorias = QGridLayout(self.view.frame_PRODUCTOS)
        else:
            self.layout_categorias = self.view.frame_PRODUCTOS.layout()

        # Capturamos el layout de la página activa del stackedWidget de la vista
        if not self.view.stackedWidget.currentWidget().layout():
            self.layout_productos = QGridLayout(self.view.stackedWidget.currentWidget())
        else:
            self.layout_productos = self.view.stackedWidget.currentWidget().layout()

        # ¡Arrancar la generación dinámica de categorías usando tu lógica!
        self.dibujar_categorias()

    def dibujar_categorias(self):
        """Genera los botones de categorías en el panel superior usando los datos del Modelo"""
        columnas_maximas = 4
        fila = 0
        columna = 0

        # Pedimos las categorías directamente a la base de datos (Modelo)
        categorias = self.model.obtener_categorias()

        for cat in categorias:
            boton_cat = QPushButton()
            boton_cat.setMinimumSize(110, 75)

            # Construimos la ruta de la imagen
            ruta_imagen = f"imagenes/{cat['id']}.jpg"

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

            # Al pulsar la categoría, cargamos sus productos a través del presentador
            boton_cat.clicked.connect(lambda checked, c_id=cat["id"]: self.dibujar_productos(c_id))

            # Añadir al panel pasándole el layout de la vista
            self.layout_categorias.addWidget(boton_cat, fila, columna)

            columna += 1
            if columna >= columnas_maximas:
                columna = 0
                fila += 1

    def limpiar_productos(self):
        """Limpia los widgets del layout de productos"""
        while self.layout_productos.count():
            item = self.layout_productos.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def dibujar_productos(self, categoria_id):
        """Genera los botones de productos filtrados al pulsar una categoría"""
        self.limpiar_productos()

        # Pedimos los productos filtrados al Modelo de forma limpia
        productos_filtrados = self.model.obtener_productos_por_categoria(categoria_id)

        columnas_maximas = 4
        fila, columna = 0, 0

        for prod in productos_filtrados:
            boton_prod = QPushButton()
            boton_prod.setMinimumSize(120, 90)

            ruta_imagen = f"imagenes/{prod['id']}.jpg"

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

            # Acción al pulsar el producto vinculada al método de este Presentador
            boton_prod.clicked.connect(lambda checked, p=prod: self.producto_pulsado(p))

            self.layout_productos.addWidget(boton_prod, fila, columna)

            columna += 1
            if columna >= columnas_maximas:
                columna = 0
                fila += 1

    def producto_pulsado(self, producto):
        """Maneja el evento de selección de un producto"""
        print(f"Añadido al ticket: {producto['nombre']} - {producto['precio']}€")