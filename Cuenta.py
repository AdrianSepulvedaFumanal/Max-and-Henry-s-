import sys
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QGridLayout,
                             QPushButton, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QLabel,
                             QHeaderView, QDialog, QListWidget, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.uic import loadUi


class TPVApp(QMainWindow):
    def __init__(self, rol="camarero"):
        super().__init__()
        self.rol = rol  # Guardamos el rol ('admin' o 'camarero') viene desde el Login
        self.rol_elegido = rol  # Control interno para cambios dinámicos de usuario
        self.total_actual = 0.0  # Rastreador de dinero acumulado de la mesa activa

        # 1. Cargamos tu interfaz gráfica
        loadUi("Diseño.ui", self)
        self.datos_tpv = self.cargar_json()

        # 2. Tarifas y suplementos fijos
        self.tarifas = {"interior": 0.0, "terraza": 0.30}

        # 3. GENERACIÓN DE MESAS FUERA DEL JSON (Directamente en Python)
        self.mesas = {}
        for i in range(1, 16):
            nombre_mesa = f"Mesa {i}"
            # De la 1 a la 10 son Interior, de la 11 a la 15 son Terraza
            zona_mesa = "interior" if i <= 10 else "terraza"
            self.mesas[nombre_mesa] = {"ticket": {}, "historial": [], "zona": zona_mesa}

        self.mesa_actual = None
        self.botones_mesas = {}

        # 4. Preparar el Layout de los productos
        self.layout_productos = self.stackedWidget.currentWidget().layout()
        if not self.layout_productos:
            self.layout_productos = QGridLayout(self.stackedWidget.currentWidget())

        # 5. Inicializar paneles visuales (Aquí se crean los botones dinámicamente)
        self.configurar_panel_factura()
        self.configurar_panel_mesas()

        # 6. Dibujar las categorías
        self.layout_categorias = self.frame_PRODUCTOS.layout()
        if not self.layout_categorias:
            self.layout_categorias = QGridLayout(self.frame_PRODUCTOS)

        self.dibujar_categorias_dinamicas()

        # Seleccionar la Mesa 1 automáticamente al arrancar
        self.seleccionar_mesa("Mesa 1")

    def cargar_json(self):
        try:
            with open("BASEDATOS.json", "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except json.JSONDecodeError:
            QMessageBox.warning(self, "Error de Base de Datos",
                                "El archivo BASEDATOS.json tiene un error de formato. Revisa que las llaves estén bien cerradas.")
            return {"categorias": [], "productos": []}

    def guardar_json(self):
        datos_a_guardar = {
            "categorias": self.datos_tpv.get("categorias", self.datos_tpv.get("categories", [])),
            "productos": self.datos_tpv.get("productos", [])
        }
        with open("BASEDATOS.json", "w", encoding="utf-8") as archivo:
            json.dump(datos_a_guardar, archivo, indent=2, ensure_ascii=False)

    def configurar_panel_factura(self):
        layout_factura = self.frame_FACTURA.layout()
        if not layout_factura:
            layout_factura = QVBoxLayout(self.frame_FACTURA)

        # Añadimos margen general al panel para que respire
        layout_factura.setContentsMargins(10, 10, 10, 10)
        layout_factura.setSpacing(10)

        if hasattr(self, 'btn_fondo_2'):
            self.btn_fondo_2.deleteLater()

        # --- TABLA DE FACTURA (Un poco más compacta) ---
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

        # --- BLOQUE INFERIOR DE CONTROL DE CUENTA ---
        layout_inferior_bloque = QVBoxLayout()
        layout_inferior_bloque.setSpacing(12)  # Separación elegante entre filas

        # 0. Fila Notificación superior
        self.lbl_notificacion = QLabel()
        self.lbl_notificacion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_notificacion.setMinimumHeight(35)
        self.lbl_notificacion.setStyleSheet(
            "background-color: #34495e; color: #ecf0f1; font-weight: bold; border-radius: 5px; font-size: 13px;")

        # 1. FILA: TOTAL A PAGAR (+ botón admin si corresponde)
        layout_fila_total = QHBoxLayout()
        self.lbl_total = QLabel("SELECCIONE MESA")
        self.lbl_total.setStyleSheet("color: #e67e22; font-size: 24px; font-weight: bold; padding-left: 2px;")
        layout_fila_total.addWidget(self.lbl_total)
        layout_fila_total.addStretch()

        # CORRECCIÓN: El botón se crea SIEMPRE para que viva en memoria pase lo que pase
        self.btn_admin_panel = QPushButton("⚙️ ADMIN")
        self.btn_admin_panel.setMinimumSize(90, 38)
        self.btn_admin_panel.setStyleSheet("""
                    QPushButton { background-color: #d35400; color: white; font-weight: bold; font-size: 12px; border-radius: 5px; }
                    QPushButton:hover { background-color: #e67e22; }
                """)
        self.btn_admin_panel.clicked.connect(self.abrir_panel_administracion)
        layout_fila_total.addWidget(self.btn_admin_panel)

        # Lo ocultamos o mostramos de inmediato según el rol de arranque actual
        self.btn_admin_panel.setVisible(self.rol == "admin")

        # 2. FILA: ACCIONES PRINCIPALES (BORRAR Y COBRAR)
        layout_fila_acciones = QHBoxLayout()
        layout_fila_acciones.setSpacing(10)

        self.btn_borrar_ultimo = QPushButton("🗑️ BORRAR ÚLTIMO")
        self.btn_borrar_ultimo.setMinimumHeight(42)
        self.btn_borrar_ultimo.setStyleSheet("""
            QPushButton { background-color: #e74c3c; color: white; font-weight: bold; font-size: 13px; border-radius: 5px; border: none; }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.btn_borrar_ultimo.clicked.connect(self.borrar_ultimo_producto)

        self.btn_cobrar = QPushButton("💰 COBRAR CUENTA")
        self.btn_cobrar.setMinimumHeight(42)
        self.btn_cobrar.setStyleSheet("""
            QPushButton { background-color: #27ae60; color: white; font-weight: bold; font-size: 13px; border-radius: 5px; border: none; }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.btn_cobrar.clicked.connect(self.finalizar_cuenta)

        layout_fila_acciones.addWidget(self.btn_borrar_ultimo, stretch=1)
        layout_fila_acciones.addWidget(self.btn_cobrar, stretch=1)

        # 3. FILA INFERIOR: HERRAMIENTAS ADICIONALES (DIVIDIR Y CAMBIAR EMPLEADO)
        layout_fila_herramientas = QHBoxLayout()
        layout_fila_herramientas.setSpacing(10)

        self.btn_dividir = QPushButton("➗ DIVIDIR CUENTA")
        self.btn_dividir.setMinimumHeight(40)
        self.btn_dividir.setStyleSheet("""
            QPushButton { background-color: #8e44ad; color: white; font-weight: bold; font-size: 13px; border-radius: 5px; border: none; }
            QPushButton:hover { background-color: #9b59b6; }
        """)
        self.btn_dividir.clicked.connect(self.llamar_dividir_cuenta)

        self.btn_cambiar_usuario = QPushButton("🔄 CAMBIAR EMPLEADO")
        self.btn_cambiar_usuario.setMinimumHeight(40)
        self.btn_cambiar_usuario.setStyleSheet("""
            QPushButton { background-color: #2980b9; color: white; font-weight: bold; font-size: 13px; border-radius: 5px; border: none; }
            QPushButton:hover { background-color: #3498db; }
        """)
        self.btn_cambiar_usuario.clicked.connect(self.llamar_cambio_usuario)

        layout_fila_herramientas.addWidget(self.btn_dividir, stretch=1)
        layout_fila_herramientas.addWidget(self.btn_cambiar_usuario, stretch=1)

        # --- ENSAMBLAJE DE LAS CAPAS ---
        layout_inferior_bloque.addWidget(self.lbl_notificacion)
        layout_inferior_bloque.addLayout(layout_fila_total)
        layout_inferior_bloque.addLayout(layout_fila_acciones)
        layout_inferior_bloque.addLayout(layout_fila_herramientas)

        # Distribuimos el espacio vertical (65% para la tabla, 35% para los botones de control)
        layout_factura.addWidget(self.tabla_factura, stretch=65)
        layout_factura.addLayout(layout_inferior_bloque, stretch=35)

    def configurar_panel_mesas(self):
        if hasattr(self, "frame_MESAS"):
            contenedor_mesas = self.frame_MESAS
        else:
            contenedor_mesas = self.frame_FACTURA

        layout_mesas_grid = contenedor_mesas.layout()
        if not layout_mesas_grid:
            layout_mesas_grid = QGridLayout(contenedor_mesas)

        lista_mesas_dinamicas = list(self.mesas.keys())
        columnas_maximas = 5

        for indice, nombre_m in enumerate(lista_mesas_dinamicas):
            btn_m = QPushButton(nombre_m)
            btn_m.setMinimumSize(65, 40)
            btn_m.clicked.connect(lambda checked, name=nombre_m: self.seleccionar_mesa(name))
            self.botones_mesas[nombre_m] = btn_m

            fila_m = indice // columnas_maximas
            col_m = indice % columnas_maximas
            layout_mesas_grid.addWidget(btn_m, fila_m, col_m)

        self.actualizar_estilos_mesas()

    def seleccionar_mesa(self, nombre_mesa):
        self.mesa_actual = nombre_mesa
        zona = self.mesas[nombre_mesa]["zona"].upper()
        self.lbl_notificacion.setText(f"📋 [{self.rol.upper()}] Gestionando {nombre_mesa} ({zona})")

        if zona == "TERRAZA":
            self.lbl_notificacion.setStyleSheet(
                "background-color: #e67e22; color: white; border-radius: 5px; padding: 4px; font-weight: bold;")
        else:
            self.lbl_notificacion.setStyleSheet(
                "background-color: #2980b9; color: white; border-radius: 5px; padding: 4px; font-weight: bold;")

        self.actualizar_tabla_factura()
        self.actualizar_estilos_mesas()

    def actualizar_estilos_mesas(self):
        for nombre_m, btn in self.botones_mesas.items():
            tiene_productos = len(self.mesas[nombre_m]["ticket"]) > 0
            es_la_actual = (self.mesa_actual == nombre_m)
            es_terraza = self.mesas[nombre_m]["zona"] == "terraza"

            if tiene_productos:
                bg_color = "#e74c3c"
                text_color = "#ffffff"
            else:
                bg_color = "#e67e22" if es_terraza else "#34495e"
                text_color = "#ffffff" if es_terraza else "#bdc3c7"

            border = "2.5px solid #2980b9" if es_la_actual else "1px solid #2c3e50"
            font_weight = "bold" if es_la_actual else "normal"

            estilo = "QPushButton { background-color: " + bg_color + "; color: " + text_color + "; border: " + border + "; font-weight: " + font_weight + "; border-radius: 5px; font-size: 11px; } "
            estilo += "QPushButton:hover { background-color: #2c3e50; color: white; }"
            btn.setStyleSheet(estilo)

    def limpiar_panel_categorias(self):
        while self.layout_categorias.count():
            item = self.layout_categorias.takeAt(0)
            widget = item.widget()
            if widget is not None: widget.deleteLater()

    def dibujar_categorias_dinamicas(self):
        self.limpiar_panel_categorias()
        columnas_maximas = 4
        fila, columna = 0, 0
        clave_cat = "categorias" if "categorias" in self.datos_tpv else "categories"

        if clave_cat in self.datos_tpv:
            for cat in self.datos_tpv[clave_cat]:
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
                    columna = 0;
                    fila += 1

    def limpiar_panel_productos(self):
        while self.layout_productos.count():
            item = self.layout_productos.takeAt(0)
            widget = item.widget()
            if widget is not None: widget.deleteLater()

    def dibujar_productos(self, categoria_id):
        self.limpiar_panel_productos()
        productos_filtrados = [p for p in self.datos_tpv.get("productos", []) if p["categoria_id"] == categoria_id]
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
                columna = 0;
                fila += 1

    def producto_pulsado(self, producto):
        if not self.mesa_actual:
            return

        prod_id = producto["id"]
        precio_base = float(producto["precio"])
        mesa_data = self.mesas[self.mesa_actual]

        zona_actual = mesa_data["zona"]
        suplemento = self.tarifas.get(zona_actual, 0.0)
        precio_final = precio_base + suplemento

        mesa_data["historial"].append(prod_id)

        if prod_id in mesa_data["ticket"]:
            mesa_data["ticket"][prod_id]["cantidad"] += 1
        else:
            nombre_ticket = producto["nombre"]
            if suplemento > 0:
                nombre_ticket += f" (+{suplemento:.2f})"
            mesa_data["ticket"][prod_id] = {"nombre": nombre_ticket, "precio": precio_final, "cantidad": 1}

        self.actualizar_tabla_factura()
        self.actualizar_estilos_mesas()

    def borrar_ultimo_producto(self):
        if not self.mesa_actual: return
        mesa_data = self.mesas[self.mesa_actual]
        if not mesa_data["historial"]: return
        ultimo_id = mesa_data["historial"].pop()
        if ultimo_id in mesa_data["ticket"]:
            mesa_data["ticket"][ultimo_id]["cantidad"] -= 1
            if mesa_data["ticket"][ultimo_id]["cantidad"] <= 0:
                del mesa_data["ticket"][ultimo_id]
        self.actualizar_tabla_factura()
        self.actualizar_estilos_mesas()

    def actualizar_tabla_factura(self):
        self.tabla_factura.setRowCount(0)
        total_general = 0.0
        if self.mesa_actual:
            ticket_actual = self.mesas[self.mesa_actual]["ticket"]
            for prod_id, info in ticket_actual.items():
                fila = self.tabla_factura.rowCount()
                self.tabla_factura.insertRow(fila)
                subtotal = info["precio"] * info["cantidad"]
                total_general += subtotal
                item_nombre = QTableWidgetItem(info["nombre"])
                item_cant = QTableWidgetItem(str(info["cantidad"]))
                item_precio = QTableWidgetItem(f"{subtotal:.2f}€")
                font = item_nombre.font();
                font.setPointSize(11)
                item_nombre.setFont(font);
                item_cant.setFont(font);
                item_precio.setFont(font)
                item_cant.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item_precio.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.tabla_factura.setItem(fila, 0, item_nombre)
                self.tabla_factura.setItem(fila, 1, item_cant)
                self.tabla_factura.setItem(fila, 2, item_precio)

            self.total_actual = total_general
            self.lbl_total.setText(f"TOTAL: {total_general:.2f}€")
            self.lbl_total.setStyleSheet("color: #2ecc71; font-size: 26px; font-weight: bold; padding-left: 2px;")
        else:
            self.total_actual = 0.0
            self.lbl_total.setText("SELECCIONE MESA")
            self.lbl_total.setStyleSheet("color: #e67e22; font-size: 24px; font-weight: bold; padding-left: 2px;")

    def finalizar_cuenta(self):
        if not self.mesa_actual: return
        mesa_data = self.mesas[self.mesa_actual]
        if not mesa_data["ticket"]: return
        total = sum(info["precio"] * info["cantidad"] for info in mesa_data["ticket"].values())
        self.lbl_notificacion.setText(f"💰 Cuenta Cerrada con éxito: {self.mesa_actual} pagó {total:.2f}€")
        self.lbl_notificacion.setStyleSheet(
            "background-color: #27ae60; color: white; border-radius: 5px; padding: 4px; font-weight: bold;")
        mesa_data["ticket"].clear()
        mesa_data["historial"].clear()
        self.actualizar_tabla_factura()
        self.actualizar_estilos_mesas()

    def abrir_panel_administracion(self):
        dialogo = QDialog(self)
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
            clave_cat = "categorias" if "categorias" in self.datos_tpv else "categories"
            if clave_cat in self.datos_tpv:
                for c in self.datos_tpv[clave_cat]:
                    lista_items.addItem(f"CATEGORIA: {c['nombre']} (ID: {c['id']})")

            lista_items.addItem("")
            lista_items.addItem("--- [ PRODUCTOS ] ---")
            for p in self.datos_tpv.get("productos", []):
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
                    clave_cat = "categorias" if "categorias" in self.datos_tpv else "categories"
                    if clave_cat not in self.datos_tpv: self.datos_tpv[clave_cat] = []
                    self.datos_tpv[clave_cat].append({"id": cat_id.lower().strip(), "nombre": nombre.upper().strip()})
                    self.guardar_json()
                    refrescar_lista_admin()
                    self.dibujar_categorias_dinamicas()

        def accion_add_producto():
            nombre, ok1 = QInputDialog.getText(dialogo, "Nuevo Producto", "Nombre del artículo:")
            if ok1 and nombre:
                precio, ok2 = QInputDialog.getDouble(dialogo, "Nuevo Producto", "Precio base (€):", 1.0, 0.0, 100.0, 2)
                if ok2:
                    cat_id, ok3 = QInputDialog.getText(dialogo, "Nuevo Producto", "ID Categoría a la que pertenece:")
                    if ok3 and cat_id:
                        p_id = nombre.lower().replace(" ", "_")
                        if "productos" not in self.datos_tpv: self.datos_tpv["productos"] = []
                        self.datos_tpv["productos"].append({
                            "id": p_id,
                            "categoria_id": cat_id.lower().strip(),
                            "nombre": nombre.upper().strip(),
                            "precio": precio
                        })
                        self.guardar_json()
                        refrescar_lista_admin()
                        self.limpiar_panel_productos()

        def accion_eliminar():
            item_seleccionado = lista_items.currentItem()
            if not item_seleccionado: return
            texto = item_seleccionado.text()

            if "ID:" in texto:
                partes = texto.split("ID: ")
                id_a_borrar = partes[1].split(")")[0].split(" |")[0].strip()

                if "CATEGORIA:" in texto:
                    clave_cat = "categorias" if "categorias" in self.datos_tpv else "categories"
                    self.datos_tpv[clave_cat] = [c for c in self.datos_tpv[clave_cat] if c["id"] != id_a_borrar]
                elif "PRODUCTO:" in texto:
                    self.datos_tpv["productos"] = [p for p in self.datos_tpv["productos"] if p["id"] != id_a_borrar]

                self.guardar_json()
                refrescar_lista_admin()
                self.dibujar_categorias_dinamicas()
                self.limpiar_panel_productos()

        btn_add_cat.clicked.connect(accion_add_categoria)
        btn_add_prod.clicked.connect(accion_add_producto)
        btn_eliminar.clicked.connect(accion_eliminar)

        layout_botones.addWidget(btn_add_cat)
        layout_botones.addWidget(btn_add_prod)
        layout_botones.addWidget(btn_eliminar)
        layout_principal.addLayout(layout_botones)

        dialogo.exec()

    # --- LÓGICA MODULAR DE ENLACE DE SCRIPTS EXTERNOS ---
    def llamar_dividir_cuenta(self):
        modulo_dividir = __import__("Dividir cuenta")
        modulo_dividir.abrir_dividir_cuenta(self)

    def llamar_cambio_usuario(self):
        modulo_cambio = __import__("Cambio de usuario")
        modulo_cambio.abrir_cambio_usuario(self)

        if hasattr(self, 'rol_elegido'):
            self.rol = self.rol_elegido

            # CORRECCIÓN: Forzamos de inmediato al botón a actualizar su visibilidad en pantalla
            if hasattr(self, 'btn_admin_panel'):
                self.btn_admin_panel.setVisible(self.rol == "admin")

            if self.mesa_actual:
                self.seleccionar_mesa(self.mesa_actual)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = TPVApp(rol="admin")
    ventana.show()
    sys.exit(app.exec())