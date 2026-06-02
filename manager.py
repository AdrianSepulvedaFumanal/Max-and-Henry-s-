class AppManager:
    def __init__(self):
        self.tables = []
        self.products = []

    # MESAS
    def create_table(self, name):
        self.tables.append({"name": name, "account": []})
        print("Mesa creada:", name)

    def delete_table(self, name):
        self.tables = [t for t in self.tables if t["name"] != name]
        print("Mesa eliminada:", name)

    # PRODUCTOS
    def create_product(self, name, category):
        self.products.append({"name": name, "category": category})
        print("Producto creado:", name)

    def delete_product(self, name):
        self.products = [p for p in self.products if p["name"] != name]
        print("Producto eliminado:", name)