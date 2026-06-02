# Creamos los botones dinámicamente uno a uno
for prod in productos_filtrados:
    # 1. Creamos el botón (esta vez sin texto, ya que la imagen habla por sí sola)
    boton = QPushButton()
    boton.setMinimumSize(120, 90)  # Ajusta al tamaño que quieras en tu cuadrícula

    # 2. Construimos la ruta de la imagen usando el ID del producto
    ruta_imagen = f"imagenes/{prod['id']}.jpg"

    # 3. Aplicamos el diseño mediante StyleSheet (¡Aquí ocurre la magia!)
    # Usamos 'border-image' para que la foto ocupe el 100% del botón de forma limpia
    boton.setStyleSheet(f"""
        QPushButton {{
            border-image: url({ruta_imagen});
            border-radius: 5px;
            border: 1px solid #333333;
        }}
        QPushButton:pressed {{
            border: 2px solid #00FF00; /* Resalta en verde al pulsar */
        }}
    """)

    # 4. Guardamos los datos del producto dentro del propio botón para saber cuál se pulsa
    boton.clicked.connect(lambda checked, p=prod: self.producto_pulsado(p))

    # 5. Lo añadimos a la cuadrícula (malla)
    self.layout_productos.addWidget(boton, fila, columna)

    # Control de filas y columnas de la cuadrícula
    columna += 1
    if columna >= columnas_maximas:
        columna = 0
        fila += 1