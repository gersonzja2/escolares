try:
    import pywhatkit
    import pyautogui
    HAS_PYWHATKIT = True
except ImportError:
    HAS_PYWHATKIT = False
import socket
import time
import os
import webbrowser
from urllib.parse import quote
import logging

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
            # Implementación robusta con validación visual opcional
            # 1. Definir ruta de la imagen de referencia (botón enviar)
            # Se asume que existe una carpeta 'assets' en src o raíz
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Ajustar ruta: src/backend/.. -> src/assets/send_button.png
            img_path = os.path.join(base_dir, "..", "assets", "send_button.png")
            
            # 2. Abrir WhatsApp Web
            url = f"https://web.whatsapp.com/send?phone={numero}&text={quote(mensaje)}"
            webbrowser.open(url)
            
            # 3. Lógica de espera inteligente
            tiempo_maximo = 60
            inicio = time.time()
            enviado = False
            
            # Verificar si tenemos la imagen para validación visual
            if os.path.exists(img_path):
                logging.info("Iniciando validación visual para envío...")
                while time.time() - inicio < tiempo_maximo:
                    try:
                        # Busca el botón en pantalla (requiere opencv para confidence, sino exact match)
                        location = pyautogui.locateOnScreen(img_path, confidence=0.8)
                        if location:
                            time.sleep(0.5)
                            pyautogui.press('enter')
                            enviado = True
                            break
                    except Exception:
                        pass # Reintentar
                    time.sleep(1)
            else:
                # Fallback: Espera fija si no hay imagen configurada
                logging.warning(f"Imagen {img_path} no encontrada. Usando espera fija (20s).")
                time.sleep(20)
                pyautogui.press('enter')
                enviado = True

            # 4. Cerrar pestaña tras envío
            if enviado:
                time.sleep(5) # Esperar confirmación visual de salida
                pyautogui.hotkey('ctrl', 'w')
                return True
            
            logging.error("Tiempo de espera agotado en WhatsApp.")
            return False
        except Exception as e:
            logging.error(f"Error enviando WhatsApp: {e}")
            return False