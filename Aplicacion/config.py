"""
Configuración del sistema de control remoto
"""

# Configuración de red
ESP32_IP = "192.168.50.190"  # IP del ESP32 (por defecto en modo AP)
ESP32_PORT = 9000  # Puerto del servidor en el ESP32

# Configuración de la interfaz
WINDOW_TITLE = "Control Remoto - Carrito ESP32"
WINDOW_WIDTH = 700  # Aumentado para el panel de monitoreo
WINDOW_HEIGHT = 700
BACKGROUND_COLOR = "#2c3e50"

# Colores de botones
BUTTON_COLOR = "#3498db"
BUTTON_ACTIVE_COLOR = "#2980b9"
BUTTON_TEXT_COLOR = "white"

# Comandos de dirección
CMD_FORWARD = "FORWARD"
CMD_BACKWARD = "BACKWARD"
CMD_LEFT = "LEFT"
CMD_RIGHT = "RIGHT"
CMD_STOP = "STOP"

# Comandos de velocidad
CMD_SPEED_LOW = "SPEED_LOW"
CMD_SPEED_HIGH = "SPEED_HIGH"
CMD_SPEED_UP = "SPEED_UP"
CMD_SPEED_DOWN = "SPEED_DOWN"

# Velocidades (valores PWM 0-255)
SPEED_LOW = 150
SPEED_HIGH = 255
SPEED_MIN = 0
SPEED_MAX = 255
SPEED_STEP = 25  # Incremento/decremento por paso

# Configuración de monitoreo
STATS_UPDATE_INTERVAL = 500  # ms - Intervalo de actualización de estadísticas
LOG_MAX_LINES = 10  # Número máximo de líneas en el log
LATENCY_WARNING_MS = 100  # ms - Umbral de advertencia de latencia
PACKET_LOSS_WARNING = 5  # % - Umbral de advertencia de pérdida de paquetes

# Configuración de Twilio (SMS)
# Cargar desde variables de entorno por seguridad
import os
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_FROM = os.getenv("TWILIO_PHONE_FROM", "")
TWILIO_PHONE_TO = os.getenv("TWILIO_PHONE_TO", "")

# Configuración de alertas
COLLISION_COOLDOWN = 10  # Segundos entre notificaciones de colisión
