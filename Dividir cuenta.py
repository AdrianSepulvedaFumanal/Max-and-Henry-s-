from PyQt6.QtWidgets import QInputDialog, QMessageBox


def abrir_dividir_cuenta(self):
    # 1. Recuperar el total actual de la cuenta activa.
    # (Sustituye 'self.total_actual' por la variable exacta donde guardes el precio de la mesa)
    try:
        total = self.total_actual
    except AttributeError:
        QMessageBox.warning(self, "Error", "No hay una cuenta cargada o activa.")
        return

    if total <= 0:
        QMessageBox.warning(self, "Operación Inválida", "La cuenta actual está vacía.")
        return

    # 2. Abrir ventanita pidiendo el número de comensales
    comensales, ok = QInputDialog.getInt(
        self,
        "Dividir Cuenta",
        "¿Entre cuántas personas se va a dividir la cuenta?",
        value=2,  # Valor por defecto
        min=1,  # Mínimo 1 persona
        max=100  # Máximo 100 personas
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