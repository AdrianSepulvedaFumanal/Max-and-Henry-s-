def __init__(self, view: MainView, model: DataBaseModel):
    self.view = view
    self.model = model

    self.botones_mesas = {}

    # 1. Forzar una limpieza absoluta de layouts viejos en el contenedor de categorías
    if self.view.frame_PRODUCTOS.layout() is not None:
        # Si existía un layout viejo del .ui, lo destruimos para que no interfiera
        import sip
        sip.delete(self.view.frame_PRODUCTOS.layout())

    self.layout_categorias = QGridLayout(self.view.frame_PRODUCTOS)
    self.view.frame_PRODUCTOS.setLayout(self.layout_categorias)

    # 2. Forzar limpieza absoluta en la página actual del stackedWidget para los productos
    widget_actual_productos = self.view.stackedWidget.currentWidget()
    if widget_actual_productos.layout() is not None:
        # Destruimos el layout viejo que viene bugeado del .ui tras el Login
        import sip
        sip.delete(widget_actual_productos.layout())

    self.layout_productos = QGridLayout(widget_actual_productos)
    widget_actual_productos.setLayout(self.layout_productos)

    # Ajustamos márgenes limpios
    self.layout_categorias.setContentsMargins(5, 5, 5, 5)
    self.layout_productos.setContentsMargins(5, 5, 5, 5)

    # 3. Configurar y pintar las mesas en su panel
    self.configurar_panel_mesas()

    # 4. Conectar los botones fijos del panel lateral a sus funciones
    self.view.btn_borrar_ultimo.clicked.connect(self.borrar_ultimo_producto)
    self.view.btn_cobrar.clicked.connect(self.finalizar_cuenta)
    self.view.btn_admin_panel.clicked.connect(self.abrir_panel_administracion)
    self.view.btn_dividir.clicked.connect(self.llamar_dividir_cuenta)
    self.view.btn_cambiar_usuario.clicked.connect(self.llamar_cambio_usuario)

    # 5. Forzar visibilidad del botón ADMIN según el rol inicial del modelo
    self.view.btn_admin_panel.setVisible(self.model.rol_actual == "admin")

    # 6. Dibujar categorías iniciales y seleccionar la Mesa 1 por defecto
    self.dibujar_categorias()
    self.seleccionar_mesa("Mesa 1")