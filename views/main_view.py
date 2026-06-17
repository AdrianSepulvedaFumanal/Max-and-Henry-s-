from PyQt6.QtWidgets import QMainWindow, QTableWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi


class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        # Cargar la interfaz limpia desde el archivo .ui
        loadUi("Diseño.ui", self)

        # Referencias globales para los componentes que crearemos dinámicamente
        self.tabla_factura = None
        self.lbl_notificacion = None
        self.lbl_total = None
        self.btn_admin_panel = None
        self.btn_borrar_ultimo = None
        self.btn_cobrar = None
        self.btn_dividir = None
        self.btn_cambiar_usuario = None

        # Inicializar los paneles visuales fijos
        self.configurar_panel_factura()

    def mostrar_pantalla(self):
        """Muestra la ventana principal maximizada"""
        self.showMaximized()

    def configurar_panel_factura(self):
        """Monta la estructura visual del ticket izquierdo con todos sus estilos"""
        layout_factura = self.frame_FACTURA.layout()
        if not layout_factura:
            layout_factura = QVBoxLayout(self.frame_FACTURA)

        layout_factura.setContentsMargins(10, 10, 10, 10)
        layout_factura.setSpacing(10)

        # --- TABLA DE LA FACTURA ---
        self.tabla_factura = QTableWidget()
        self.tabla_factura.setColumnCount(3)
        self.tabla_factura.setHorizontalHeaderLabels(["Producto", "Cant.", "Precio"])

        header = self.tabla_factura.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

        self.tabla_factura.setStyleSheet("""
            QTableWidget {
                background-color: #242424; color: white; gridline-color: #3a3a3a;
                border: 1px solid #333333; font-size: 14px; border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #1a1a1a; color: #ffffff; padding: 6px;
                border: 1px solid #333333; font-weight: bold; font-size: 13px;
            }
        """)
        self.tabla_factura.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_factura.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        # --- BLOQUE INFERIOR DE BOTONES Y TEXTOS ---
        layout_inferior_bloque = QVBoxLayout()
        layout_inferior_bloque.setSpacing(12)

        # Notificación superior de la mesa activa
        self.lbl_notificacion = QLabel("SELECCIONE UNA MESA PARA EMPEZAR")
        self.lbl_notificacion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_notificacion.setMinimumHeight(35)
        self.lbl_notificacion.setStyleSheet(
            "background-color: #34495e; color: #ecf0f1; font-weight: bold; border-radius: 5px; font-size: 13px;")

        # Fila del Total y Botón de Admin
        layout_fila_total = QHBoxLayout()
        self.lbl_total = QLabel("TOTAL: 0.00€")
        self.lbl_total.setStyleSheet("color: #e67e22; font-size: 24px; font-weight: bold; padding-left: 2px;")
        layout_fila_total.addWidget(self.lbl_total)
        layout_fila_total.addStretch()

        self.btn_admin_panel = QPushButton("⚙️ ADMIN")
        self.btn_admin_panel.setMinimumSize(90, 38)
        self.btn_admin_panel.setStyleSheet("""
            QPushButton { background-color: #d35400; color: white; font-weight: bold; font-size: 12px; border-radius: 5px; }
            QPushButton:hover { background-color: #e67e22; }
        """)
        layout_fila_total.addWidget(self.btn_admin_panel)

        # Acciones Principales (Borrar y Cobrar)
        layout_fila_acciones = QHBoxLayout()
        layout_fila_acciones.setSpacing(10)

        self.btn_borrar_ultimo = QPushButton("🗑️ BORRAR ÚLTIMO")
        self.btn_borrar_ultimo.setMinimumHeight(42)
        self.btn_borrar_ultimo.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: white; font-weight: bold; font-size: 13px; border-radius: 5px; }
            QPushButton:hover { background-color: #c0392b; }
        """)

        self.btn_cobrar = QPushButton("💰 COBRAR CUENTA")
        self.btn_cobrar.setMinimumHeight(42)
        self.btn_cobrar.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; font-weight: bold; font-size: 13px; border-radius: 5px; }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        layout_fila_acciones.addWidget(self.btn_borrar_ultimo, stretch=1)
        layout_fila_acciones.addWidget(self.btn_cobrar, stretch=1)

        # Herramientas de abajo (Dividir y Cambiar Empleado)
        layout_fila_herramientas = QHBoxLayout()
        layout_fila_herramientas.setSpacing(10)

        self.btn_dividir = QPushButton("➗ DIVIDIR CUENTA")
        self.btn_dividir.setMinimumHeight(40)
        self.btn_dividir.setStyleSheet("""
            QPushButton { background-color: #8e44ad; color: white; font-weight: bold; font-size: 13px; border-radius: 5px; }
            QPushButton:hover { background-color: #9b59b6; }
        """)

        self.btn_cambiar_usuario = QPushButton("🔄 CAMBIAR EMPLEADO")
        self.btn_cambiar_usuario.setMinimumHeight(40)
        self.btn_cambiar_usuario.setStyleSheet("""
            QPushButton { background-color: #2980b9; color: white; font-weight: bold; font-size: 13px; border-radius: 5px; }
            QPushButton:hover { background-color: #3498db; }
        """)
        layout_fila_herramientas.addWidget(self.btn_dividir, stretch=1)
        layout_fila_herramientas.addWidget(self.btn_cambiar_usuario, stretch=1)

        # Ensamblar todo el lateral izquierdo
        layout_inferior_bloque.addWidget(self.lbl_notificacion)
        layout_inferior_bloque.addLayout(layout_fila_total)
        layout_inferior_bloque.addLayout(layout_fila_acciones)
        layout_inferior_bloque.addLayout(layout_fila_herramientas)

        layout_factura.addWidget(self.tabla_factura, stretch=65)
        layout_factura.addLayout(layout_inferior_bloque, stretch=35)