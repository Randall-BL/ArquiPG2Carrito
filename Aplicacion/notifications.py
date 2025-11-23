"""
Módulo de notificaciones por SMS usando Twilio
"""

import time
from typing import Optional
import config


class TwilioNotifier:
    """Clase para enviar notificaciones SMS usando Twilio"""
    
    def __init__(self):
        self.last_notification_time = 0
        self.twilio_client = None
        self._initialize_twilio()
    
    def _initialize_twilio(self):
        """Inicializa el cliente de Twilio"""
        try:
            from twilio.rest import Client
            
            # Verificar que las credenciales estén configuradas
            if (config.TWILIO_ACCOUNT_SID == "tu_account_sid_aqui" or 
                config.TWILIO_AUTH_TOKEN == "tu_auth_token_aqui"):
                print("⚠ Credenciales de Twilio no configuradas en config.py")
                print("  Edita config.py y agrega tus credenciales de Twilio")
                self.twilio_client = None
                return
            
            self.twilio_client = Client(
                config.TWILIO_ACCOUNT_SID,
                config.TWILIO_AUTH_TOKEN
            )
            print("✓ Cliente Twilio inicializado")
            
        except ImportError:
            print("⚠ Twilio no está instalado. Ejecuta: pip install twilio")
            self.twilio_client = None
        except Exception as e:
            print(f"✗ Error al inicializar Twilio: {e}")
            self.twilio_client = None
    
    def send_collision_alert(self) -> bool:
        """
        Envía una alerta de colisión por SMS
        Returns:
            bool: True si el SMS se envió exitosamente
        """
        # Verificar cooldown para evitar spam
        current_time = time.time()
        if current_time - self.last_notification_time < config.COLLISION_COOLDOWN:
            print(f"⏳ Esperando cooldown ({config.COLLISION_COOLDOWN}s entre notificaciones)")
            return False
        
        if not self.twilio_client:
            print("✗ Cliente Twilio no disponible")
            return False
        
        try:
            # Mensaje de alerta
            message_body = (
                "🚨 ALERTA DE COLISIÓN 🚨\n\n"
                "El carrito ESP32 ha detectado una colisión.\n"
                "El sistema se ha detenido automáticamente.\n\n"
                f"Hora: {time.strftime('%H:%M:%S')}\n"
                f"Fecha: {time.strftime('%d/%m/%Y')}"
            )
            
            # Enviar SMS
            message = self.twilio_client.messages.create(
                body=message_body,
                from_=config.TWILIO_PHONE_FROM,
                to=config.TWILIO_PHONE_TO
            )
            
            print(f"✓ SMS enviado exitosamente")
            print(f"  SID: {message.sid}")
            print(f"  A: {config.TWILIO_PHONE_TO}")
            
            # Actualizar tiempo de última notificación
            self.last_notification_time = current_time
            
            return True
            
        except Exception as e:
            print(f"✗ Error al enviar SMS: {e}")
            return False
    
    def send_custom_message(self, message: str, phone_to: Optional[str] = None) -> bool:
        """
        Envía un mensaje personalizado por SMS
        Args:
            message: Mensaje a enviar
            phone_to: Número de teléfono destino (opcional, usa config por defecto)
        Returns:
            bool: True si el SMS se envió exitosamente
        """
        if not self.twilio_client:
            print("✗ Cliente Twilio no disponible")
            return False
        
        destination = phone_to or config.TWILIO_PHONE_TO
        
        try:
            msg = self.twilio_client.messages.create(
                body=message,
                from_=config.TWILIO_PHONE_FROM,
                to=destination
            )
            
            print(f"✓ SMS enviado a {destination}")
            print(f"  SID: {msg.sid}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error al enviar SMS: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Verifica si Twilio está configurado correctamente"""
        return self.twilio_client is not None
    
    def test_connection(self) -> bool:
        """
        Prueba la conexión con Twilio enviando un mensaje de prueba
        Returns:
            bool: True si la conexión funciona
        """
        if not self.twilio_client:
            return False
        
        try:
            # Verificar cuenta
            account = self.twilio_client.api.accounts(config.TWILIO_ACCOUNT_SID).fetch()
            print(f"✓ Conexión exitosa con Twilio")
            print(f"  Cuenta: {account.friendly_name}")
            print(f"  Estado: {account.status}")
            return True
        except Exception as e:
            print(f"✗ Error de conexión con Twilio: {e}")
            return False
