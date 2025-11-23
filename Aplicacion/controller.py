"""
Módulo controlador principal que coordina la GUI y la comunicación
"""

import config
import json
import os
from datetime import datetime
from communication import ESP32Communication
from gui import ControlGUI
from monitoring import CommunicationMonitor
from notifications import TwilioNotifier


class CarController:
    """Controlador principal del sistema de control remoto"""
    
    LOG_FILE = "esp32_logs.json"  # Archivo donde se guardan los logs
    
    def __init__(self):
        self.monitor = CommunicationMonitor()
        self.comm = ESP32Communication(
            monitor=self.monitor, 
            collision_callback=self._handle_collision_alert,
            speed_callback=self._handle_speed_update,
            log_callback=self._handle_esp32_logs
        )
        self.notifier = TwilioNotifier()  # Sistema de notificaciones
        self.gui = ControlGUI(
            on_direction_callback=self.handle_direction,
            on_speed_callback=self.handle_speed,
            on_connect_callback=self.handle_connect,
            on_disconnect_callback=self.handle_disconnect
        )
        self.current_pwm = config.SPEED_LOW  # PWM que se envía al ESP32 (0-255)
        self.current_speed_real = 0.0  # Velocidad real medida por MPU6050 (cm/s)
        self.esp32_logs_buffer = []  # Buffer local de logs del ESP32
        
        # Cargar logs existentes si hay
        self._load_logs_from_file()
        
        # Actualizar displays iniciales
        self.gui.update_pwm_display(self.current_pwm)
        self.gui.update_speed_display(self.current_speed_real)
        
        # Iniciar actualización periódica de estadísticas
        self._schedule_stats_update()
        self._schedule_log_request()
        
    def handle_direction(self, command: str):
        """
        Maneja comandos de dirección
        Args:
            command: Comando de dirección (FORWARD, BACKWARD, LEFT, RIGHT, STOP)
        """
        if self.comm.is_connected():
            self.comm.send_command(command)
        else:
            print("⚠ No conectado. Conecta primero al ESP32")
            
    def handle_speed(self, command: str):
        """
        Maneja comandos de velocidad
        Args:
            command: Comando de velocidad (SPEED_LOW, SPEED_HIGH, SPEED_UP, SPEED_DOWN)
        """
        if command == config.CMD_SPEED_LOW:
            self.current_pwm = config.SPEED_LOW
            print(f"🐌 Velocidad BAJA: {config.SPEED_LOW}")
        elif command == config.CMD_SPEED_HIGH:
            self.current_pwm = config.SPEED_HIGH
            print(f"🚀 Velocidad ALTA: {config.SPEED_HIGH}")
        elif command == config.CMD_SPEED_UP:
            # Incrementar velocidad
            new_speed = min(self.current_pwm + config.SPEED_STEP, config.SPEED_MAX)
            if new_speed != self.current_pwm:
                self.current_pwm = new_speed
                print(f"⬆ Velocidad incrementada: {self.current_pwm}")
            else:
                print(f"⚠ Velocidad máxima alcanzada: {config.SPEED_MAX}")
        elif command == config.CMD_SPEED_DOWN:
            # Decrementar velocidad
            new_speed = max(self.current_pwm - config.SPEED_STEP, config.SPEED_MIN)
            if new_speed != self.current_pwm:
                self.current_pwm = new_speed
                print(f"⬇ Velocidad decrementada: {self.current_pwm}")
            else:
                print(f"⚠ Velocidad mínima alcanzada: {config.SPEED_MIN}")
        
        # Actualizar display de PWM
        self.gui.update_pwm_display(self.current_pwm)
        
        # Enviar comando al ESP32
        if self.comm.is_connected():
            # Para SPEED_UP y SPEED_DOWN, enviamos el valor específico
            if command in [config.CMD_SPEED_UP, config.CMD_SPEED_DOWN]:
                # Crear comando con el valor exacto
                speed_command = f"SPEED_SET:{self.current_pwm}"
                self.comm.send_command(speed_command)
            else:
                self.comm.send_command(command)
            
    def handle_connect(self):
        """Maneja la conexión con el ESP32"""
        print("Intentando conectar al ESP32...")
        
        # Resetear estadísticas
        self.monitor.reset()
        self.gui.clear_log()
        
        success = self.comm.connect()
        
        if success:
            self.gui.update_connection_status(True)
            self.gui.show_info("Conexión", f"Conectado exitosamente a {config.ESP32_IP}")
            self.gui.add_log_message("=== Conexión Establecida ===")
            self.gui.add_log_message(f"IP: {config.ESP32_IP}:{config.ESP32_PORT}")
            
            # Consultar la velocidad actual del ESP32
            import time
            time.sleep(0.5)  # Dar tiempo para establecer la conexión
            self.comm.send_command("GET_SPEED")
        else:
            self.gui.update_connection_status(False)
            self.gui.show_error(
                "Error de Conexión",
                f"No se pudo conectar al ESP32 en {config.ESP32_IP}:{config.ESP32_PORT}\n\n"
                "Verifica que:\n"
                "• El ESP32 esté encendido\n"
                "• Estés conectado a la red WiFi del ESP32\n"
                "• La dirección IP sea correcta"
            )
            self.gui.add_log_message("✗ Error al conectar")
            
    def handle_disconnect(self):
        """Maneja la desconexión del ESP32"""
        self.comm.disconnect()
        self.gui.update_connection_status(False)
        self.gui.add_log_message("=== Desconectado ===")
        print("Desconectado del ESP32")
    
    def _schedule_stats_update(self):
        """Programa la actualización periódica de estadísticas"""
        if not self.gui.is_closed:
            self._update_statistics()
            # Reprogramar para la próxima actualización
            self.gui.root.after(config.STATS_UPDATE_INTERVAL, self._schedule_stats_update)
    
    def _update_statistics(self):
        """Actualiza las estadísticas en la GUI"""
        if self.comm.is_connected():
            stats = self.monitor.get_statistics_summary()
            self.gui.update_statistics(stats)
            
            # Actualizar log con mensajes recientes
            log_messages = self.monitor.get_log_messages()
            # Solo mostrar los últimos mensajes nuevos
            for message in log_messages[-5:]:  # Últimos 5 mensajes
                pass  # Ya se agregan en tiempo real
    
    def _handle_collision_alert(self):
        """Maneja la alerta de colisión"""
        print("\n⚠️ ¡COLISIÓN DETECTADA!")
        
        # Detener el carrito inmediatamente
        self.comm.send_command(config.CMD_STOP)
        
        # Mostrar alerta en la GUI
        self.gui.add_log_message("⚠️ ¡COLISIÓN DETECTADA!")
        
        # Enviar notificación SMS
        success = self.notifier.send_collision_alert()
        
        if success:
            print("✓ Notificación SMS enviada")
            self.gui.add_log_message("✓ SMS enviado a +50662494299")
        else:
            print("✗ Error al enviar notificación SMS")
            self.gui.add_log_message("✗ Error al enviar SMS")
    
    def _handle_speed_update(self, speed: int):
        """Maneja la actualización de velocidad real desde el ESP32 (MPU6050)"""
        try:
            # Convertir a float si viene como entero o string
            speed_value = float(speed)
            print(f"📊 Velocidad real MPU6050: {speed_value:.2f} cm/s")
            self.current_speed_real = speed_value
            # Actualizar solo el display de velocidad real, no el PWM
            self.gui.update_speed_display(self.current_speed_real)
        except (ValueError, TypeError) as e:
            print(f"Error al procesar velocidad: {e}")
    
    def _handle_esp32_logs(self, logs: list):
        """Maneja los logs recibidos del ESP32"""
        # Actualizar buffer local (mantener solo los últimos 10)
        self.esp32_logs_buffer = logs[-10:] if len(logs) > 10 else logs
        
        # Guardar en archivo
        self._save_logs_to_file()
        
        # Mostrar en GUI
        self.gui.add_log_message("--- Logs ESP32 ---")
        for log in self.esp32_logs_buffer:
            self.gui.add_log_message(f"🔧 {log}")
        self.gui.add_log_message("------------------")
    
    def _save_logs_to_file(self):
        """Guarda los logs en un archivo JSON"""
        try:
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "logs": self.esp32_logs_buffer,
                "total_logs": len(self.esp32_logs_buffer)
            }
            
            with open(self.LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Logs guardados en {self.LOG_FILE}")
        except Exception as e:
            print(f"✗ Error al guardar logs: {e}")
    
    def _load_logs_from_file(self):
        """Carga los logs desde el archivo si existe"""
        try:
            if os.path.exists(self.LOG_FILE):
                with open(self.LOG_FILE, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
                    self.esp32_logs_buffer = log_data.get("logs", [])
                    print(f"✓ Cargados {len(self.esp32_logs_buffer)} logs desde {self.LOG_FILE}")
            else:
                print(f"ℹ No se encontró archivo de logs previo")
        except Exception as e:
            print(f"✗ Error al cargar logs: {e}")
            self.esp32_logs_buffer = []
    
    def _schedule_log_request(self):
        """Programa la solicitud periódica de logs del ESP32"""
        if not self.gui.is_closed:
            if self.comm.is_connected():
                self.comm.request_logs()
            # Reprogramar para la próxima solicitud (cada 5 segundos)
            self.gui.root.after(5000, self._schedule_log_request)
        
    def run(self):
        """Inicia la aplicación"""
        print("=" * 50)
        print("Control Remoto para Carrito ESP32")
        print("=" * 50)
        print(f"IP del ESP32: {config.ESP32_IP}:{config.ESP32_PORT}")
        print(f"Archivo de logs: {self.LOG_FILE}")
        print("\nInstrucciones:")
        print("1. Conecta tu PC a la red WiFi del ESP32")
        print("2. Haz clic en 'Conectar'")
        print("3. Usa los botones o el teclado para controlar")
        print("=" * 50)
        
        try:
            self.gui.run()
        finally:
            # Guardar logs finales antes de cerrar
            if self.esp32_logs_buffer:
                self._save_logs_to_file()
            self.handle_disconnect()
            print("\n¡Hasta luego!")
