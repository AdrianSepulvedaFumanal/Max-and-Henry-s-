from PyQt6.QtWidgets import QInputDialog, QMessageBox

def abrir_dividir_cuenta(self):
    # 1. Recuperamos la mesa y el ticket desde los datos que nos prestó el presentador
    mesa_actual = getattr(self, 'mesa_actual', None)
    mesas = getattr(self, 'mesas', {})

    if not mesa_actual or mesa_actual not in mesas:
        QMessageBox.warning(self, "Error", "No hay una cuenta cargada o activa.")
        return

    ticket_actual = mesas[mesa_actual]["ticket"]

    # Si el ticket no tiene productos, avisamos
    if not ticket_actual:
        QMessageBox.warning(self, "Operación Inválida", "La cuenta actual está vacía.")
        return

    # Calculamos el total de la mesa sumando precio * cantidad de cada producto
    total = sum(info["precio"] * info["cantidad"] for info in ticket_actual.values())

    # 2. Abrir ventanita pidiendo el número de comensales (añadimos el total en el texto para que quede mejor)
    comensales, ok = QInputDialog.getInt(
        self,
        "Dividir Cuenta",
        f"Total a dividir: {total:.2f}€\n¿Entre cuántas personas?",
        value=2,  # Valor por defecto
        min=1,    # Mínimo 1 persona
        max=100   # Máximo 100 personas
    )

    # 3. Si el usuario pulsa "OK" en la ventana, hacemos la matemática
    if ok:
        pago_por_persona = total / comensales

        # Mostramos el desglose en un cuadro informativo elegante
        QMessageBox.information(
            self,
            "Cuenta Dividida",
            f"💰 Total Mesa: {total:.2f}€\n"
            f"👥 Comensales: {comensales}\n\n"
            f"💳 Cada persona paga: {pago_por_persona:.2f}€"
        )