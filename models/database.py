import json
import os


class DataBaseModel:
    def __init__(self):
        self.ruta_json = "BASEDATOS.json"
        self.datos_tpv = self.cargar_json()

        # Tarifas y suplementos fijos del negocio
        self.tarifas = {"interior": 0.0, "terraza": 0.30}

        # Rol y sesión activa del sistema
        self.rol_actual = "admin"  # Por defecto arranca como admin, luego cambiará

        # ESTRUCTURA DE MESAS (Generación dinámica inicial en memoria)
        self.mesas = {}
        for i in range(1, 16):
            nombre_mesa = f"Mesa {i}"
            zona_mesa = "interior" if i <= 10 else "terraza"
            self.mesas[nombre_mesa] = {"ticket": {}, "historial": [], "zona": zona_mesa}

        self.mesa_actual = "Mesa 1"  # Mesa seleccionada por defecto

    def cargar_json(self):
        """Carga de forma segura el archivo de la base de datos"""
        if not os.path.exists(self.ruta_json):
            return {"categorias": [], "productos": []}
        try:
            with open(self.ruta_json, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except json.JSONDecodeError:
            return {"categorias": [], "productos": []}

    def guardar_json(self):
        """Guarda las categorías y productos actuales en el JSON"""
        datos_a_guardar = {
            "categorias": self.datos_tpv.get("categorias", []),
            "productos": self.datos_tpv.get("productos", [])
        }
        with open(self.ruta_json, "w", encoding="utf-8") as archivo:
            json.dump(datos_a_guardar, archivo, indent=2, ensure_ascii=False)

    def obtener_categorias(self):
        return self.datos_tpv.get("categorias", [])

    def obtener_productos_por_categoria(self, categoria_id):
        return [p for p in self.datos_tpv.get("productos", []) if p["categoria_id"] == categoria_id]

    # --- NUEVOS MÉTODOS DE GESTIÓN DE ESTADO ---
    def obtener_mesas(self):
        return self.mesas

    def obtener_mesa_actual(self):
        return self.mesa_actual

    def cambiar_mesa_actual(self, nombre_mesa):
        if nombre_mesa in self.mesas:
            self.mesa_actual = nombre_mesa

    def agregar_producto_a_mesa(self, producto):
        """Añade un producto al ticket de la mesa activa calculando suplementos"""
        if not self.mesa_actual:
            return

        mesa_data = self.mesas[self.mesa_actual]
        prod_id = producto["id"]
        precio_base = float(producto["precio"])

        # Calcular precio final con el suplemento de la zona de la mesa
        zona_actual = mesa_data["zona"]
        suplemento = self.tarifas.get(zona_actual, 0.0)
        precio_final = precio_base + suplemento

        # Guardamos en el historial de pulsaciones para poder borrar el último después
        mesa_data["historial"].append(prod_id)

        # Agregamos o incrementamos cantidad en el ticket de la mesa
        if prod_id in mesa_data["ticket"]:
            mesa_data["ticket"][prod_id]["cantidad"] += 1
        else:
            nombre_ticket = producto["nombre"]
            if suplemento > 0:
                nombre_ticket += f" (+{suplemento:.2f})"
            mesa_data["ticket"][prod_id] = {
                "nombre": nombre_ticket,
                "precio": precio_final,
                "cantidad": 1
            }

    def eliminar_ultimo_producto_mesa(self):
        """Elimina la última pulsación del ticket de la mesa activa"""
        if not self.mesa_actual:
            return
        mesa_data = self.mesas[self.mesa_actual]
        if not mesa_data["historial"]:
            return

        ultimo_id = mesa_data["historial"].pop()
        if ultimo_id in mesa_data["ticket"]:
            mesa_data["ticket"][ultimo_id]["cantidad"] -= 1
            if mesa_data["ticket"][ultimo_id]["cantidad"] <= 0:
                del mesa_data["ticket"][ultimo_id]

    def vaciar_mesa_actual(self):
        """Limpia el ticket e historial de la mesa activa (para cuando se cobra)"""
        if self.mesa_actual:
            self.mesas[self.mesa_actual]["ticket"].clear()
            self.mesas[self.mesa_actual]["historial"].clear()