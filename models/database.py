import json
import os

class DataBaseModel:
    def __init__(self, ruta_archivo="BASEDATOS.json"):
        # Apunta directamente al archivo en la raíz del proyecto
        self.ruta_archivo = ruta_archivo
        self.datos = self.cargar_json()

    def cargar_json(self):
        try:
            if os.path.exists(self.ruta_archivo):
                with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                    return json.load(archivo)
        except json.JSONDecodeError:
            pass
        # Si falla o no existe, devuelve una estructura limpia para no romper el programa
        return {"categorias": [], "productos": []}

    def guardar_json(self):
        with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(self.datos, archivo, indent=2, ensure_ascii=False)

    def obtener_categorias(self):
        return self.datos.get("categorias", self.datos.get("categories", []))

    def obtener_productos_por_categoria(self, categoria_id):
        return [p for p in self.datos.get("productos", []) if p["categoria_id"] == categoria_id]

    def agregar_categoria(self, cat_id, nombre):
        clave_cat = "categorias" if "categorias" in self.datos else "categories"
        if clave_cat not in self.datos:
            self.datos[clave_cat] = []
        self.datos[clave_cat].append({"id": cat_id, "nombre": nombre})
        self.guardar_json()

    def agregar_producto(self, prod_id, cat_id, nombre, precio):
        if "productos" not in self.datos:
            self.datos["productos"] = []
        self.datos["productos"].append({
            "id": prod_id,
            "categoria_id": cat_id,
            "nombre": nombre,
            "precio": precio
        })
        self.guardar_json()

    def eliminar_elemento(self, elemento_id, es_categoria=True):
        if es_categoria:
            clave_cat = "categorias" if "categorias" in self.datos else "categories"
            self.datos[clave_cat] = [c for c in self.datos[clave_cat] if c["id"] != elemento_id]
        else:
            self.datos["productos"] = [p for p in self.datos["productos"] if p["id"] != elemento_id]
        self.guardar_json()