try:
    import pywhatkit
    HAS_PYWHATKIT = True
except ImportError:
    HAS_PYWHATKIT = False
import socket

class WhatsAppService:
    @staticmethod
    def hay_internet():
        """Verifica si hay conexión a internet intentando conectar a Google."""
        try:
            socket.create_connection(("www.google.com", 80), timeout=3)
            return True
        except OSError:
            return False

    @staticmethod
    def enviar_mensaje(numero: str, mensaje: str) -> bool:
        """Abre WhatsApp Web y envía el mensaje."""
        if not HAS_PYWHATKIT:
            print("Error: La librería 'pywhatkit' no está instalada. Ejecute: pip install pywhatkit")
            return False

        try:
            # wait_time: tiempo para cargar la página (20s)
            # tab_close: cerrar pestaña al terminar
            pywhatkit.sendwhatmsg_instantly(
                phone_no=numero, 
                message=mensaje, 
                wait_time=15, 
                tab_close=True,
                close_time=5
            )
            return True
        except Exception as e:
            print(f"Error enviando WhatsApp: {e}")
            return False