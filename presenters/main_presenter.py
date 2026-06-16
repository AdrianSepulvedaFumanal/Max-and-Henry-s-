import os
from PyQt6.QtWidgets import QPushButton, QGridLayout, QTableWidgetItem, QDialog, QVBoxLayout, QLabel, QListWidget, \
    QHBoxLayout, QInputDialog
from PyQt6.QtCore import Qt
from models.database import DataBaseModel
from views.main_view import MainView


class MainPresenter:
    def __init__(self, view: MainView, model: DataBaseModel):
        self.view = view
        self.model = model

        self.botones_mesas = {}

        # 1. Asegurar layouts dinámicos en los contenedores de la Vista
        if self.view.frame_PRODUCTOS.layout() is None:
            self.layout_categorias = QGridLayout(self.view.frame_PRODUCTOS)
        else:
            self.layout_categorias = self.view.frame_PRODUCTOS.layout()

        # Forzamos un QGridLayout limpio en la página actual del stackedWidget para los productos
        widget_actual_productos = self.view.stackedWidget.currentWidget()
        if widget_actual_productos.layout() is None:
            self.layout_productos = QGridLayout(widget_actual_productos)
        else:
            self.layout_productos = widget_actual_productos.layout()

        # 2. Configurar y pintar las mesas en su panel (Corregido: Llamada única)
        self.configurar_panel_mesas()

        # 3. Conectar los botones fijos del panel lateral a sus funciones
        self.view.btn_borrar_ultimo.clicked.connect(self.borrar_ultimo_producto)
        self.view.btn_cobrar.clicked.connect(self.finalizar_cuenta)
        self.view.btn_admin_panel.clicked.connect(self.abrir_panel_administracion)
        self.view.btn_dividir.clicked.connect(self.llamar_dividir_cuenta)
        self.view.btn_cambiar_usuario.clicked.connect(self.llamar_cambio_usuario)

        # 4. Forzar visibilidad del botón ADMIN según el rol inicial del modelo
        self.view.btn_admin_panel.setVisible(self.model.rol_actual == "admin")

        # 5. Dibujar categorías iniciales y seleccionar la Mesa 1 por defecto
        self.dibujar_categorias()
        self.seleccionar_mesa("Mesa 1")

    # --- SISTEMA DE MESAS ---
    def configurar_panel_mesas(self):
        contenedor_mesas = getattr(self.view, "frame_MESAS", self.view.frame_FACTURA)
        layout_mesas_grid = contenedor_mesas.layout() or QGridLayout(contenedor_mesas)

        mesas_dict = self.model.obtener_mesas()
        columnas_maximas = 5

        for indice, nombre_m in enumerate(mesas_dict.keys()):
            btn_m = QPushButton(nombre_m)
            btn_m.setMinimumSize(65, 40)
            btn_m.clicked.connect(lambda checked, name=nombre_m: self.seleccionar_mesa(name))
            self.botones_mesas[nombre_m] = btn_m

            fila_m = indice // columnas_maximas
            col_m = indice % columnas_maximas
            layout_mesas_grid.addWidget(btn_m, fila_m, col_m)

        self.actualizar_estilos_mesas()

    def seleccionar_mesa(self, nombre_mesa):
        self.model.cambiar_mesa_actual(nombre_mesa)
        mesa_data = self.model.obtener_mesas()[nombre_mesa]
        zona = mesa_data["zona"].upper()

        self.view.lbl_notificacion.setText(f"📋 [{self.model.rol_actual.upper()}] Gestionando {nombre_mesa} ({zona})")

        if zona == "TERRAZA":
            self.view.lbl_notificacion.setStyleSheet(
                "background-color: #e67e22; color: white; border-radius: 5px; padding: 4px; font-weight: bold;")
        else:
            self.view.lbl_notificacion.setStyleSheet(
                "background-color: #2980b9; color: white; border-radius: 5px; padding: 4px; font-weight: bold;")

        self.actualizar_tabla_factura()
        self.actualizar_estilos_mesas()

    def actualizar_estilos_mesas(self):
        mesa_actual = self.model.obtener_mesa_actual()
        for nombre_m, btn in self.botones_mesas.items():
            mesa_data = self.model.obtener_mesas()[nombre_m]
            tiene_productos = len(mesa_data["ticket"]) > 0
            es_la_actual = (mesa_actual == nombre_m)
            es_terraza = mesa_data["zona"] == "terraza"

            if tiene_productos:
                bg_color = "#e74c3c"
                text_color = "#ffffff"
            else:
                bg_color = "#e67e22" if es_terraza else "#34495e"
                text_color = "#ffffff" if es_terraza else "#bdc3c7"

            border = "2.5px solid #2980b9" if es_la_actual else "1px solid #2c3e50"
            font_weight = "bold" if es_la_actual else "normal"

            estilo = f"QPushButton {{ background-color: {bg_color}; color: {text_color}; border: {border}; font-weight: {font_weight}; border-radius: 5px; font-size: 11px; }} "
            estilo += "QPushButton:hover { background-color: #2c3e50; color: white; }"
            btn.setStyleSheet(estilo)

    # --- CATEGORÍAS Y PRODUCTOS ---
    def dibujar_categorias(self):
        while self.layout_categorias.count():
            item = self.layout_categorias.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        columnas_maximas = 4
        fila, columna = 0, 0
        categorias = self.model.obtener_categorias()

        for cat in categorias:
            boton_cat = QPushButton()
            boton_cat.setMinimumSize(110, 75)
            ruta_imagen = f"imagenes/{cat['id']}.jpg"
            if os.path.exists(ruta_imagen):
                boton_cat.setStyleSheet(
                    f"QPushButton {{ border-image: url({ruta_imagen}); border-radius: 5px; border: 1px solid #333333; }}")
            else:
                boton_cat.setText(cat["nombre"])
                boton_cat.setStyleSheet(
                    "background-color: #1abc9c; color: white; font-weight: bold; border-radius: 5px; font-size: 13px;")

            boton_cat.clicked.connect(lambda checked, c_id=cat["id"]: self.dibujar_productos(c_id))
            self.layout_categorias.addWidget(boton_cat, fila, columna)
            columna += 1
            if columna >= columnas_maximas:
                columna = 0
                fila += 1

    def dibujar_productos(self, categoria_id):
        while self.layout_productos.count():
            item = self.layout_productos.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        productos_filtrados = self.model.obtener_productos_por_categoria(categoria_id)
        columnas_maximas = 4
        fila, columna = 0, 0

        for prod in productos_filtrados:
            boton = QPushButton()
            boton.setMinimumSize(120, 90)
            ruta_imagen = f"imagenes/{prod['id']}.jpg"
            if os.path.exists(ruta_imagen):
                boton.setStyleSheet(
                    f"QPushButton {{ border-image: url({ruta_imagen}); border-radius: 5px; border: 1px solid #333333; }}")
            else:
                boton.setText(f"{prod['nombre']}\n{prod['precio']}€")
                boton.setStyleSheet(
                    "background-color: #2c3e50; color: white; font-weight: bold; border-radius: 5px; font-size: 11px;")

            boton.clicked.connect(lambda checked, p=prod: self.producto_pulsado(p))
            self.layout_productos.addWidget(boton, fila, columna)
            columna += 1
            if columna >= columnas_maximas:
                columna = 0
                fila += 1

    def producto_pulsado(self, producto):
        self.model.agregar_producto_a_mesa(producto)
        self.actualizar_tabla_factura()
        self.actualizar_estilos_mesas()

    def borrar_ultimo_producto(self):
        self.model.eliminar_ultimo_producto_mesa()
        self.actualizar_tabla_factura()
        self.actualizar_estilos_mesas()

    # --- RENDERIZADO DEL TICKET ---
    def actualizar_tabla_factura(self):
        self.view.tabla_factura.setRowCount(0)
        total_general = 0.0
        mesa_actual = self.model.obtener_mesa_actual()

        if mesa_actual:
            ticket_actual = self.model.obtener_mesas()[mesa_actual]["ticket"]
            for prod_id, info in ticket_actual.items():
                fila = self.view.tabla_factura.rowCount()
                self.view.tabla_factura.insertRow(fila)
                subtotal = info["precio"] * info["cantidad"]
                total_general += subtotal

                item_nombre = QTableWidgetItem(info["nombre"])
                item_cant = QTableWidgetItem(str(info["cantidad"]))
                item_precio = QTableWidgetItem(f"{subtotal:.2f}€")

                font = item_nombre.font()
                font.setPointSize(11)
                item_nombre.setFont(font)
                item_cant.setFont(font)
                item_precio.setFont(font)

                item_cant.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

                self.view.tabla_factura.setItem(fila, 0, item_nombre)
                self.view.tabla_factura.setItem(fila, 1, item_cant)
                self.view.tabla_factura.setItem(fila, 2, item_precio)

            self.view.lbl_total.setText(f"TOTAL: {total_general:.2f}€")
            self.view.lbl_total.setStyleSheet("color: #2ecc71; font-size: 26px; font-weight: bold; padding-left: 2px;")
        else:
            self.view.lbl_total.setText("SELECCIONE MESA")
            self.view.lbl_total.setStyleSheet("color: #e67e22; font-size: 24px; font-weight: bold; padding-left: 2px;")

    def finalizar_cuenta(self):
        mesa_actual = self.model.obtener_mesa_actual()
        if not mesa_actual: return
        mesa_data = self.model.obtener_mesas()[mesa_actual]
        if not mesa_data["ticket"]: return

        total = sum(info["precio"] * info["cantidad"] for info in mesa_data["ticket"].values())
        self.view.lbl_notificacion.setText(f"💰 Cuenta Cerrada con éxito: {mesa_actual} pagó {total:.2f}€")
        self.view.lbl_notificacion.setStyleSheet(
            "background-color: #27ae60; color: white; border-radius: 5px; padding: 4px; font-weight: bold;")

        self.model.vaciar_mesa_actual()
        self.actualizar_tabla_factura()
        self.actualizar_estilos_mesas()

    # --- PANEL DE ADMINISTRACIÓN ---
    def abrir_panel_administracion(self):
        dialogo = QDialog(self.view)
        dialogo.setWindowTitle("🛠️ Panel de Control - Configuración del Local")
        dialogo.resize(500, 400)
        dialogo.setStyleSheet("background-color: #1e1e1e; color: white;")
        layout_principal = QVBoxLayout(dialogo)

        lbl_info = QLabel("Selecciona un elemento para borrar, o pulsa añadir:")
        lbl_info.setStyleSheet("font-weight: bold; color: #f1c40f;")
        layout_principal.addWidget(lbl_info)

        lista_items = QListWidget()
        lista_items.setStyleSheet("background-color: #2c3e50; color: white; font-size: 13px;")

        def refrescar_lista_admin():
            lista_items.clear()
            lista_items.addItem("--- [ CATEGORÍAS ] ---")
            for c in self.model.obtener_categorias():
                lista_items.addItem(f"CATEGORIA: {c['nombre']} (ID: {c['id']})")

            lista_items.addItem("")
            lista_items.addItem("--- [ PRODUCTOS ] ---")
            for c in self.model.obtener_categorias():
                for p in self.model.obtener_productos_por_categoria(cat_id := c['id']):
                    lista_items.addItem(
                        f"PRODUCTO: {p['nombre']} - {p['precio']}€ (ID: {p['id']} | Cat: {p['categoria_id']})")

        refrescar_lista_admin()
        layout_principal.addWidget(lista_items)

        layout_botones = QHBoxLayout()
        btn_add_cat = QPushButton("➕ Nueva Categoría")
        btn_add_prod = QPushButton("➕ Nuevo Producto")
        btn_eliminar = QPushButton("🗑️ Eliminar Seleccionado")

        for btn in [btn_add_cat, btn_add_prod, btn_eliminar]:
            btn.setMinimumHeight(35)
            btn.setStyleSheet("background-color: #34495e; color: white; font-weight: bold; border-radius: 4px;")
        btn_eliminar.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; border-radius: 4px;")

        def accion_add_categoria():
            nombre, ok1 = QInputDialog.getText(dialogo, "Nueva Categoría", "Nombre de la categoría:")
            if ok1 and nombre:
                cat_id, ok2 = QInputDialog.getText(dialogo, "Nueva Categoría", "ID único (ej: cafés, tapas):")
                if ok2 and cat_id:
                    self.model.datos_tpv.setdefault("categorias", []).append(
                        {"id": cat_id.lower().strip(), "nombre": nombre.upper().strip()})
                    self.model.guardar_json()
                    refrescar_lista_admin()
                    self.dibujar_categorias()

        def accion_add_producto():
            nombre, ok1 = QInputDialog.getText(dialogo, "Nuevo Producto", "Nombre del artículo:")
            if ok1 and nombre:
                precio, ok2 = QInputDialog.getDouble(dialogo, "Nuevo Producto", "Precio base (€):", 1.0, 0.0, 100.0, 2)
                if ok2:
                    cat_id, ok3 = QInputDialog.getText(dialogo, "Nuevo Producto", "ID Categoría a la que pertenece:")
                    if ok3 and cat_id:
                        p_id = nombre.lower().replace(" ", "_")
                        self.model.datos_tpv.setdefault("productos", []).append({
                            "id": p_id, "categoria_id": cat_id.lower().strip(), "nombre": nombre.upper().strip(),
                            "precio": precio
                        })
                        self.model.guardar_json()
                        refrescar_lista_admin()
                        while self.layout_productos.count():
                            item = self.layout_productos.takeAt(0)
                            if item.widget(): item.widget().deleteLater()

        def accion_eliminar():
            item_seleccionado = lista_items.currentItem()
            if not item_seleccionado: return
            texto = item_seleccionado.text()

            if "ID:" in texto:
                id_a_borrar = texto.split("ID: ")[1].split(")")[0].split(" |")[0].strip()
                if "CATEGORIA:" in texto:
                    self.model.datos_tpv["categorias"] = [c for c in self.model.datos_tpv.get("categorias", []) if
                                                          c["id"] != id_a_borrar]
                elif "PRODUCTO:" in texto:
                    self.model.datos_tpv["productos"] = [p for p in self.model.datos_tpv.get("productos", []) if
                                                         p["id"] != id_a_borrar]

                self.model.guardar_json()
                refrescar_lista_admin()
                self.dibujar_categorias()

        btn_add_cat.clicked.connect(accion_add_categoria)
        btn_add_prod.clicked.connect(accion_add_producto)
        btn_eliminar.clicked.connect(accion_eliminar)

        layout_botones.addWidget(btn_add_cat)
        layout_botones.addWidget(btn_add_prod)
        layout_botones.addWidget(btn_eliminar)
        layout_principal.addLayout(layout_botones)
        dialogo.exec()

    def llamar_dividir_cuenta(self):
        try:
            # 1. Le "inyectamos" a la Vista los datos que el script antiguo espera encontrar
            self.view.mesa_actual = self.model.obtener_mesa_actual()
            self.view.mesas = self.model.obtener_mesas()

            # 2. Le prestamos las funciones del presentador para que el script pueda refrescar la pantalla
            self.view.actualizar_tabla_factura = self.actualizar_tabla_factura
            # Por si tu script antiguo usaba el nombre viejo o el nuevo para los estilos:
            self.view.estilos_mesas = self.actualizar_estilos_mesas
            self.view.actualizar_estilos_mesas = self.actualizar_estilos_mesas

            # 3. Llamamos al script externo pasándole self.view (¡Evita el crash porque sí es un QWidget!)
            modulo_dividir = __import__("Dividir cuenta")
            modulo_dividir.abrir_dividir_cuenta(self.view)

        except Exception as e:
            # Si hay algún error lógico en el script, lo capturamos e imprimimos sin cerrar el programa
            import traceback
            print(f"⚠️ Error al ejecutar Dividir Cuenta:\n{traceback.format_exc()}")
    def llamar_cambio_usuario(self):
        try:
            modulo_cambio = __import__("Cambio de usuario")
            # Recomendado cambiar a 'self' si el script necesita interactuar con el presentador
            modulo_cambio.abrir_cambio_usuario(self.view)

            # Al regresar, refrescamos el rol en el modelo y actualizamos visibilidad
            self.model.rol_actual = getattr(self.view, 'rol_elegido', self.model.rol_actual)
            self.view.btn_admin_panel.setVisible(self.model.rol_actual == "admin")
            self.seleccionar_mesa(self.model.obtener_mesa_actual())
        except ModuleNotFoundError:
            pass