from PyQt6.QtWidgets import QMessageBox


def abrir_cambio_usuario(parent_tpv):
    """
    Función que invoca el cambio de empleado de forma segura.
    Recibe 'parent_tpv' (que es la instancia de tu TPVApp).
    """
    try:
        # 1. Importamos tu archivo con su nuevo nombre limpio: Login.py
        import Login

        # 2. Creamos la instancia de la ventana usando el módulo Login
        dialogo_login = Login.LoginVentana()

        # 3. .exec() la abre en modo modal (pausa el TPV de fondo y espera)
        if dialogo_login.exec():
            # Si el usuario pone sus credenciales y le da a Entrar/Aceptar:
            nuevo_rol = dialogo_login.rol_elegido

            # Sincronizamos los roles en el TPV principal
            parent_tpv.rol_elegido = nuevo_rol
            parent_tpv.rol = nuevo_rol

            # Avisamos con un mensaje elegante integrado
            QMessageBox.information(parent_tpv, "Usuario Cambiado", f"Sesión iniciada como: {nuevo_rol.upper()}")

            # Controlamos el botón de ADMIN del TPV de forma dinámica
            if hasattr(parent_tpv, 'btn_admin_panel'):
                parent_tpv.btn_admin_panel.setVisible(nuevo_rol == "admin")

    except ModuleNotFoundError:
        QMessageBox.critical(parent_tpv, "Error de Sistema",
                             "No se encontró 'Login.py'. Asegúrate de haber renombrado el archivo correctamente a 'Login.py'.")
    except Exception as e:
        QMessageBox.critical(parent_tpv, "Error Crítico", f"No se pudo cambiar de usuario:\n{str(e)}")