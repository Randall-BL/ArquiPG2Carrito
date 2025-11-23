"""
Módulo de monitoreo y estadísticas de comunicación
"""

import time
from collections import deque
from typing import List, Dict
import config


class CommunicationMonitor:
    """Clase para monitorear estadísticas de comunicación"""
    
    def __init__(self):
        # Estadísticas de latencia
        self.latency_history = deque(maxlen=100)  # Últimas 100 mediciones
        self.last_command_time = 0
        self.last_response_time = 0
        
        # Estadísticas de comandos
        self.commands_sent = 0
        self.responses_received = 0
        self.commands_failed = 0
        
        # Estadísticas de ancho de banda
        self.bytes_sent = 0
        self.bytes_received = 0
        self.connection_start_time = None
        
        # Log de comunicación
        self.communication_log = deque(maxlen=config.LOG_MAX_LINES)
        
    def reset(self):
        """Reinicia todas las estadísticas"""
        self.latency_history.clear()
        self.last_command_time = 0
        self.last_response_time = 0
        self.commands_sent = 0
        self.responses_received = 0
        self.commands_failed = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.connection_start_time = None
        self.communication_log.clear()
        
    def start_connection(self):
        """Marca el inicio de una conexión"""
        self.connection_start_time = time.time()
        self.add_log("✓ Conexión establecida")
        
    def command_sent(self, command: str):
        """Registra el envío de un comando"""
        self.last_command_time = time.time()
        self.commands_sent += 1
        self.bytes_sent += len(command.encode()) + 1  # +1 por el \n
        timestamp = time.strftime("%H:%M:%S")
        self.add_log(f"[{timestamp}] → {command}")
        
    def response_received(self, response: str):
        """Registra la recepción de una respuesta"""
        self.last_response_time = time.time()
        self.responses_received += 1
        self.bytes_received += len(response.encode())
        
        # Calcular latencia
        if self.last_command_time > 0:
            latency = (self.last_response_time - self.last_command_time) * 1000  # en ms
            self.latency_history.append(latency)
        
        timestamp = time.strftime("%H:%M:%S")
        self.add_log(f"[{timestamp}] ← {response}")
        
    def command_failed(self):
        """Registra un comando fallido"""
        self.commands_failed += 1
        timestamp = time.strftime("%H:%M:%S")
        self.add_log(f"[{timestamp}] ✗ Comando fallido")
        
    def add_log(self, message: str):
        """Agrega un mensaje al log"""
        self.communication_log.append(message)
        
    def get_average_latency(self) -> float:
        """Obtiene la latencia promedio en ms"""
        if not self.latency_history:
            return 0.0
        return sum(self.latency_history) / len(self.latency_history)
    
    def get_min_latency(self) -> float:
        """Obtiene la latencia mínima en ms"""
        if not self.latency_history:
            return 0.0
        return min(self.latency_history)
    
    def get_max_latency(self) -> float:
        """Obtiene la latencia máxima en ms"""
        if not self.latency_history:
            return 0.0
        return max(self.latency_history)
    
    def get_current_latency(self) -> float:
        """Obtiene la última latencia medida en ms"""
        if not self.latency_history:
            return 0.0
        return self.latency_history[-1]
    
    def get_packet_loss_rate(self) -> float:
        """Calcula la tasa de pérdida de paquetes en %"""
        total = self.commands_sent
        if total == 0:
            return 0.0
        return (self.commands_failed / total) * 100
    
    def get_reliability(self) -> float:
        """Calcula la confiabilidad en %"""
        return 100 - self.get_packet_loss_rate()
    
    def get_bandwidth(self) -> Dict[str, float]:
        """Calcula el ancho de banda en bytes/segundo"""
        if self.connection_start_time is None:
            return {"upload": 0.0, "download": 0.0, "total": 0.0}
        
        elapsed_time = time.time() - self.connection_start_time
        if elapsed_time == 0:
            return {"upload": 0.0, "download": 0.0, "total": 0.0}
        
        upload_bps = self.bytes_sent / elapsed_time
        download_bps = self.bytes_received / elapsed_time
        
        return {
            "upload": upload_bps,
            "download": download_bps,
            "total": upload_bps + download_bps
        }
    
    def get_connection_time(self) -> float:
        """Obtiene el tiempo de conexión en segundos"""
        if self.connection_start_time is None:
            return 0.0
        return time.time() - self.connection_start_time
    
    def get_log_messages(self) -> List[str]:
        """Obtiene la lista de mensajes del log"""
        return list(self.communication_log)
    
    def get_statistics_summary(self) -> Dict:
        """Obtiene un resumen completo de estadísticas"""
        bandwidth = self.get_bandwidth()
        
        return {
            "latency": {
                "current": self.get_current_latency(),
                "average": self.get_average_latency(),
                "min": self.get_min_latency(),
                "max": self.get_max_latency()
            },
            "reliability": {
                "success_rate": self.get_reliability(),
                "packet_loss": self.get_packet_loss_rate(),
                "commands_sent": self.commands_sent,
                "responses_received": self.responses_received,
                "commands_failed": self.commands_failed
            },
            "bandwidth": {
                "upload_bps": bandwidth["upload"],
                "download_bps": bandwidth["download"],
                "total_bps": bandwidth["total"],
                "bytes_sent": self.bytes_sent,
                "bytes_received": self.bytes_received
            },
            "connection": {
                "duration": self.get_connection_time()
            }
        }
