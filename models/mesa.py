class MesaModel:
    def __init__(self, numero, zona):
        self.nombre = f"Mesa {numero}"
        self.zona = zona  # "interior" o "terraza"
        self.ticket = {}  # prod_id -> {"nombre": str, "precio": float, "cantidad": int}
        self.historial = []  # Listado de IDs agregados en orden para hacer "undo"

    def agregar_producto(self, producto, suplemento):
        prod_id = producto["id"]
        precio_final = float(producto["precio"]) + suplemento

        self.historial.append(prod_id)
        if prod_id in self.ticket:
            self.ticket[prod_id]["cantidad"] += 1
        else:
            nombre_ticket = producto["nombre"]
            if suplemento > 0:
                nombre_ticket += f" (+{suplemento:.2f})"
            self.ticket[prod_id] = {
                "nombre": nombre_ticket,
                "precio": precio_final,
                "cantidad": 1
            }

    def borrar_ultimo(self):
        if not self.historial:
            return None
        ultimo_id = self.historial.pop()
        if ultimo_id in self.ticket:
            self.ticket[ultimo_id]["cantidad"] -= 1
            if self.ticket[ultimo_id]["cantidad"] <= 0:
                del self.ticket[ultimo_id]
        return ultimo_id

    def calcular_total(self):
        return sum(item["precio"] * item["cantidad"] for item in self.ticket.values())

    def vaciar_cuenta(self):
        self.ticket.clear()
        self.historial.clear()