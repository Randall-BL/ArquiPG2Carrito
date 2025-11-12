"""
Módulo de comunicación WiFi con el ESP32
"""

import socket
import time
from typing import Optional
import config


class ESP32Communication:
    """Clase para manejar la comunicación con el ESP32"""
    
    def __init__(self, monitor=None):
        self.ip = config.ESP32_IP
        self.port = config.ESP32_PORT
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.last_command = ""
        self.retry_delay = 0.1
        self.monitor = monitor  # Monitor de estadísticas
        
    def connect(self) -> bool:
        """
        Establece conexión con el ESP32
        Returns:
            bool: True si la conexión fue exitosa
        """
        try:
            if self.socket:
                self.disconnect()
                
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            self.socket.connect((self.ip, self.port))
            self.connected = True
            print(f"✓ Conectado al ESP32 en {self.ip}:{self.port}")
            
            # Notificar al monitor
            if self.monitor:
                self.monitor.start_connection()
            
            return True
        except Exception as e:
            print(f"✗ Error de conexión: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Cierra la conexión con el ESP32"""
        try:
            if self.socket:
                self.socket.close()
                self.socket = None
            self.connected = False
            print("✓ Desconectado del ESP32")
        except Exception as e:
            print(f"Error al desconectar: {e}")
    
    def send_command(self, command: str) -> bool:
        """
        Envía un comando al ESP32
        Args:
            command: Comando a enviar
        Returns:
            bool: True si el envío fue exitoso
        """
        if not self.connected:
            print("✗ No hay conexión activa")
            if self.monitor:
                self.monitor.command_failed()
            return False
        
        # Evitar enviar el mismo comando repetidamente
        if command == self.last_command and command != config.CMD_STOP:
            return True
            
        try:
            message = f"{command}\n"
            
            # Registrar envío en el monitor
            if self.monitor:
                self.monitor.command_sent(command)
            
            self.socket.sendall(message.encode())
            self.last_command = command
            print(f"→ Comando enviado: {command}")
            
            # Intentar recibir confirmación
            try:
                self.socket.settimeout(0.5)
                response = self.socket.recv(1024).decode().strip()
                if response:
                    print(f"← Respuesta: {response}")
                    # Registrar respuesta en el monitor
                    if self.monitor:
                        self.monitor.response_received(response)
            except socket.timeout:
                pass  # No hay problema si no hay respuesta
            
            return True
        except Exception as e:
            print(f"✗ Error al enviar comando: {e}")
            self.connected = False
            if self.monitor:
                self.monitor.command_failed()
            return False
    
    def is_connected(self) -> bool:
        """Verifica si está conectado"""
        return self.connected
    
    def set_ip(self, ip: str):
        """Actualiza la IP del ESP32"""
        self.ip = ip
        
    def set_monitor(self, monitor):
        """Asigna un monitor de estadísticas"""
        self.monitor = monitor
