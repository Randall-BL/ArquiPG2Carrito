"""
Módulo de interfaz gráfica con panel de monitoreo
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import Callable
import config


class ControlGUI:
    """Clase para la interfaz gráfica del control remoto con monitoreo"""
    
    def __init__(self, on_direction_callback: Callable, on_speed_callback: Callable,
                 on_connect_callback: Callable, on_disconnect_callback: Callable):
        self.on_direction = on_direction_callback
        self.on_speed = on_speed_callback
        self.on_connect = on_connect_callback
        self.on_disconnect = on_disconnect_callback
        
        self.root = tk.Tk()
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.configure(bg=config.BACKGROUND_COLOR)
        self.root.resizable(False, False)
        
        self.current_speed = "LOW"
        self.connection_status_label = None
        self.speed_display_label = None
        self.is_closed = False
        
        # Referencias para monitoreo
        self.stats_labels = {}
        self.log_text = None
        
        # Estado de la palanca (0=neutral, 1=avanzar, -1=retroceder)
        self.joystick_position = 0
        self.joystick_canvas = None
        self.joystick_handle = None
        
        # Manejar el cierre de la ventana
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self._setup_ui()
        self._setup_key_bindings()
        
    def _setup_ui(self):
        """Configura todos los elementos de la interfaz"""
        # Frame contenedor principal con dos columnas
        container = tk.Frame(self.root, bg=config.BACKGROUND_COLOR)
        container.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Columna izquierda: Controles (350px)
        left_frame = tk.Frame(container, bg=config.BACKGROUND_COLOR, width=350)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Columna derecha: Monitoreo
        right_frame = tk.Frame(container, bg="#34495e", relief='solid', borderwidth=2)
        right_frame.pack(side='right', fill='both', expand=True)
        
        self._setup_control_panel(left_frame)
        self._setup_monitoring_panel(right_frame)
        
    def _setup_control_panel(self, parent):
        """Configura el panel de controles"""
        
        # Título
        title = tk.Label(
            parent, 
            text="🚗 Control Remoto", 
            font=("Arial", 16, "bold"),
            bg=config.BACKGROUND_COLOR,
            fg="white"
        )
        title.pack(pady=(0, 5))
        
        # Estado de conexión
        self.connection_status_label = tk.Label(
            parent,
            text="● Desconectado",
            font=("Arial", 9),
            bg=config.BACKGROUND_COLOR,
            fg="#e74c3c"
        )
        self.connection_status_label.pack(pady=3)
        
        # Botones de conexión
        conn_frame = tk.Frame(parent, bg=config.BACKGROUND_COLOR)
        conn_frame.pack(pady=5)
        
        tk.Button(
            conn_frame, text="Conectar", font=("Arial", 9),
            bg="#27ae60", fg="white", width=11, height=1,
            command=self._handle_connect
        ).pack(side='left', padx=3)
        
        tk.Button(
            conn_frame, text="Desconectar", font=("Arial", 9),
            bg="#e74c3c", fg="white", width=11, height=1,
            command=self._handle_disconnect
        ).pack(side='left', padx=3)
        
        # Separador
        tk.Frame(parent, height=1, bg="#34495e").pack(fill='x', pady=8)
        
        # Controles de dirección
        tk.Label(
            parent, text="Dirección", font=("Arial", 11, "bold"),
            bg=config.BACKGROUND_COLOR, fg="white"
        ).pack(pady=(0, 5))
        
        self._create_direction_controls(parent)
        
        # Separador
        tk.Frame(parent, height=1, bg="#34495e").pack(fill='x', pady=8)
        
        # Controles de velocidad
        tk.Label(
            parent, text="Velocidad", font=("Arial", 11, "bold"),
            bg=config.BACKGROUND_COLOR, fg="white"
        ).pack(pady=(0, 5))
        
        self._create_speed_controls(parent)
        
        # Instrucciones
        tk.Label(
            parent,
            text="Palanca=Avanzar/Retroceder | Q/E=Izq/Der | Espacio=Freno",
            font=("Arial", 7),
            bg=config.BACKGROUND_COLOR,
            fg="#95a5a6"
        ).pack(side='bottom', pady=(5, 0))
        
    def _create_direction_controls(self, parent):
        """Crea la palanca y botones de dirección"""
        control_frame = tk.Frame(parent, bg=config.BACKGROUND_COLOR)
        control_frame.pack(pady=10)
        
        # Frame izquierdo: Palanca vertical
        joystick_frame = tk.Frame(control_frame, bg=config.BACKGROUND_COLOR)
        joystick_frame.pack(side='left', padx=15)
        
        tk.Label(
            joystick_frame, text="Avanzar/Retroceder", font=("Arial", 8),
            bg=config.BACKGROUND_COLOR, fg="#95a5a6"
        ).pack(pady=(0, 5))
        
        # Canvas para la palanca
        self.joystick_canvas = tk.Canvas(
            joystick_frame, width=80, height=200,
            bg="#34495e", highlightthickness=2,
            highlightbackground="#2c3e50"
        )
        self.joystick_canvas.pack()
        
        # Dibujar ranura de la palanca
        self.joystick_canvas.create_line(
            40, 20, 40, 180,
            fill="#7f8c8d", width=8
        )
        
        # Marcadores de posición
        # Avanzar (arriba)
        self.joystick_canvas.create_text(
            15, 35, text="▲", font=("Arial", 12),
            fill="#27ae60", anchor='e'
        )
        # Neutral (centro)
        self.joystick_canvas.create_text(
            15, 100, text="●", font=("Arial", 12),
            fill="#95a5a6", anchor='e'
        )
        # Retroceder (abajo)
        self.joystick_canvas.create_text(
            15, 165, text="▼", font=("Arial", 12),
            fill="#e74c3c", anchor='e'
        )
        
        # Manija de la palanca (se puede arrastrar)
        self.joystick_handle = self.joystick_canvas.create_oval(
            20, 85, 60, 115,
            fill="#3498db", outline="#2980b9", width=3
        )
        
        # Bind para arrastrar la palanca
        self.joystick_canvas.tag_bind(self.joystick_handle, '<Button-1>', self._on_joystick_click)
        self.joystick_canvas.tag_bind(self.joystick_handle, '<B1-Motion>', self._on_joystick_drag)
        self.joystick_canvas.tag_bind(self.joystick_handle, '<ButtonRelease-1>', self._on_joystick_release)
        
        # Frame derecho: Botones de giro y freno
        buttons_frame = tk.Frame(control_frame, bg=config.BACKGROUND_COLOR)
        buttons_frame.pack(side='left', padx=15)
        
        tk.Label(
            buttons_frame, text="Giro", font=("Arial", 8),
            bg=config.BACKGROUND_COLOR, fg="#95a5a6"
        ).pack(pady=(0, 5))
        
        # Botones de giro
        turn_frame = tk.Frame(buttons_frame, bg=config.BACKGROUND_COLOR)
        turn_frame.pack(pady=5)
        
        tk.Button(
            turn_frame, text="◄\nIZQ", font=("Arial", 10, "bold"),
            bg="#f39c12", fg="white", width=6, height=3,
            command=lambda: self.on_direction(config.CMD_LEFT)
        ).pack(side='left', padx=3)
        
        tk.Button(
            turn_frame, text="►\nDER", font=("Arial", 10, "bold"),
            bg="#f39c12", fg="white", width=6, height=3,
            command=lambda: self.on_direction(config.CMD_RIGHT)
        ).pack(side='left', padx=3)
        
        # Botón de freno
        tk.Label(
            buttons_frame, text="Freno", font=("Arial", 8),
            bg=config.BACKGROUND_COLOR, fg="#95a5a6"
        ).pack(pady=(10, 5))
        
        tk.Button(
            buttons_frame, text="■\nFRENO", font=("Arial", 11, "bold"),
            bg="#e74c3c", fg="white", width=14, height=2,
            command=lambda: self._handle_brake()
        ).pack()
    
    def _on_joystick_click(self, event):
        """Maneja el click en la palanca"""
        pass
    
    def _on_joystick_drag(self, event):
        """Maneja el arrastre de la palanca"""
        # Obtener coordenadas del mouse
        y = event.y
        
        # Limitar el movimiento vertical
        y = max(35, min(165, y))
        
        # Mover la manija
        self.joystick_canvas.coords(self.joystick_handle, 20, y-15, 60, y+15)
        
    def _on_joystick_release(self, event):
        """Maneja cuando se suelta la palanca - se queda en posición"""
        # Obtener la posición Y actual
        coords = self.joystick_canvas.coords(self.joystick_handle)
        y_center = (coords[1] + coords[3]) / 2
        
        # Determinar la posición final (snap a las 3 posiciones)
        if y_center < 60:  # Zona superior - AVANZAR
            final_y = 35
            new_position = 1
            self.on_direction(config.CMD_FORWARD)
        elif y_center > 140:  # Zona inferior - RETROCEDER
            final_y = 165
            new_position = -1
            self.on_direction(config.CMD_BACKWARD)
        else:  # Zona central - NEUTRAL
            final_y = 100
            new_position = 0
            self.on_direction(config.CMD_STOP)
        
        # Actualizar posición de la palanca
        self.joystick_canvas.coords(self.joystick_handle, 20, final_y-15, 60, final_y+15)
        
        # Cambiar color según posición
        if new_position == 1:
            self.joystick_canvas.itemconfig(self.joystick_handle, fill="#27ae60", outline="#229954")
        elif new_position == -1:
            self.joystick_canvas.itemconfig(self.joystick_handle, fill="#e74c3c", outline="#c0392b")
        else:
            self.joystick_canvas.itemconfig(self.joystick_handle, fill="#95a5a6", outline="#7f8c8d")
        
        self.joystick_position = new_position
    
    def _handle_brake(self):
        """Maneja el freno - detiene y resetea la palanca"""
        self.on_direction(config.CMD_STOP)
        # Resetear palanca a posición neutral
        self.joystick_canvas.coords(self.joystick_handle, 20, 85, 60, 115)
        self.joystick_canvas.itemconfig(self.joystick_handle, fill="#95a5a6", outline="#7f8c8d")
        self.joystick_position = 0
        
    def _create_dpad(self, parent):
        """DEPRECATED - Reemplazado por _create_direction_controls"""
        pass
        
    def _create_speed_controls(self, parent):
        """Crea los controles de velocidad"""
        speed_frame = tk.Frame(parent, bg=config.BACKGROUND_COLOR)
        speed_frame.pack(pady=5)
        
        # Botones preestablecidos
        preset_frame = tk.Frame(speed_frame, bg=config.BACKGROUND_COLOR)
        preset_frame.pack(pady=3)
        
        tk.Button(
            preset_frame, text="🐌 BAJA", font=("Arial", 9, "bold"),
            bg="#f39c12", fg="white", width=9, height=1,
            command=lambda: self._handle_speed_change(config.CMD_SPEED_LOW)
        ).pack(side='left', padx=3)
        
        tk.Button(
            preset_frame, text="🚀 ALTA", font=("Arial", 9, "bold"),
            bg="#e74c3c", fg="white", width=9, height=1,
            command=lambda: self._handle_speed_change(config.CMD_SPEED_HIGH)
        ).pack(side='left', padx=3)
        
        # Display de velocidad
        display_frame = tk.Frame(speed_frame, bg=config.BACKGROUND_COLOR)
        display_frame.pack(pady=5)
        
        tk.Label(
            display_frame, text="Actual:", font=("Arial", 8),
            bg=config.BACKGROUND_COLOR, fg="white"
        ).pack()
        
        self.speed_display_label = tk.Label(
            display_frame, text="150 / 255", font=("Arial", 13, "bold"),
            bg="#34495e", fg="#3498db", width=10,
            relief="sunken", padx=8, pady=3
        )
        self.speed_display_label.pack(pady=3)
        
        # Botones de ajuste
        adjust_frame = tk.Frame(speed_frame, bg=config.BACKGROUND_COLOR)
        adjust_frame.pack(pady=3)
        
        tk.Button(
            adjust_frame, text="▼ BAJAR", font=("Arial", 9, "bold"),
            bg="#95a5a6", fg="white", width=9, height=1,
            command=lambda: self._handle_speed_change(config.CMD_SPEED_DOWN)
        ).pack(side='left', padx=3)
        
        tk.Button(
            adjust_frame, text="▲ SUBIR", font=("Arial", 9, "bold"),
            bg="#27ae60", fg="white", width=9, height=1,
            command=lambda: self._handle_speed_change(config.CMD_SPEED_UP)
        ).pack(side='left', padx=3)
    
    def _setup_monitoring_panel(self, parent):
        """Configura el panel de monitoreo"""
        
        # Título del panel
        title = tk.Label(
            parent, text="📊 Monitoreo en Tiempo Real",
            font=("Arial", 12, "bold"),
            bg="#34495e", fg="white"
        )
        title.pack(pady=8, padx=5)
        
        # Frame para estadísticas
        stats_frame = tk.Frame(parent, bg="#34495e")
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        # Latencia
        self._create_stat_row(stats_frame, "⏱️ Latencia:", "latency", "0 ms")
        
        # Confiabilidad
        self._create_stat_row(stats_frame, "✓ Confiabilidad:", "reliability", "100%")
        
        # Ancho de banda
        self._create_stat_row(stats_frame, "📶 Ancho de Banda:", "bandwidth", "0 B/s")
        
        # Comandos enviados
        self._create_stat_row(stats_frame, "📤 Comandos Enviados:", "commands_sent", "0")
        
        # Paquetes perdidos
        self._create_stat_row(stats_frame, "❌ Pérdida de Paquetes:", "packet_loss", "0%")
        
        # Separador
        tk.Frame(parent, height=2, bg="#2c3e50").pack(fill='x', pady=8)
        
        # Log de comunicación
        tk.Label(
            parent, text="📝 Log de Comunicación",
            font=("Arial", 10, "bold"),
            bg="#34495e", fg="white"
        ).pack(pady=(0, 5))
        
        # Área de texto para el log
        log_frame = tk.Frame(parent, bg="#34495e")
        log_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            width=30,
            bg="#2c3e50",
            fg="#ecf0f1",
            font=("Consolas", 8),
            state='disabled',
            wrap='word'
        )
        self.log_text.pack(fill='both', expand=True)
        
    def _create_stat_row(self, parent, label_text, key, initial_value):
        """Crea una fila de estadística"""
        row_frame = tk.Frame(parent, bg="#34495e")
        row_frame.pack(fill='x', pady=3)
        
        tk.Label(
            row_frame, text=label_text,
            font=("Arial", 9),
            bg="#34495e", fg="#bdc3c7",
            anchor='w', width=18
        ).pack(side='left')
        
        value_label = tk.Label(
            row_frame, text=initial_value,
            font=("Arial", 9, "bold"),
            bg="#2c3e50", fg="#3498db",
            anchor='e', width=15,
            relief='sunken', padx=5, pady=2
        )
        value_label.pack(side='right')
        
        self.stats_labels[key] = value_label
        
    def _setup_key_bindings(self):
        """Configura los atajos de teclado"""
        # Palanca con W/S
        self.root.bind('<w>', lambda e: self._set_joystick_position(1))
        self.root.bind('<W>', lambda e: self._set_joystick_position(1))
        self.root.bind('<s>', lambda e: self._set_joystick_position(-1))
        self.root.bind('<S>', lambda e: self._set_joystick_position(-1))
        
        # Giros con Q/E
        self.root.bind('<q>', lambda e: self.on_direction(config.CMD_LEFT))
        self.root.bind('<Q>', lambda e: self.on_direction(config.CMD_LEFT))
        self.root.bind('<e>', lambda e: self.on_direction(config.CMD_RIGHT))
        self.root.bind('<E>', lambda e: self.on_direction(config.CMD_RIGHT))
        
        # Freno con espacio
        self.root.bind('<space>', lambda e: self._handle_brake())
        
        # Velocidad
        self.root.bind('1', lambda e: self._handle_speed_change(config.CMD_SPEED_LOW))
        self.root.bind('2', lambda e: self._handle_speed_change(config.CMD_SPEED_HIGH))
        self.root.bind('+', lambda e: self._handle_speed_change(config.CMD_SPEED_UP))
        self.root.bind('=', lambda e: self._handle_speed_change(config.CMD_SPEED_UP))
        self.root.bind('-', lambda e: self._handle_speed_change(config.CMD_SPEED_DOWN))
    
    def _set_joystick_position(self, position):
        """Establece la posición de la palanca mediante teclado"""
        if position == 1:  # Avanzar
            final_y = 35
            self.on_direction(config.CMD_FORWARD)
            self.joystick_canvas.itemconfig(self.joystick_handle, fill="#27ae60", outline="#229954")
        elif position == -1:  # Retroceder
            final_y = 165
            self.on_direction(config.CMD_BACKWARD)
            self.joystick_canvas.itemconfig(self.joystick_handle, fill="#e74c3c", outline="#c0392b")
        else:  # Neutral
            final_y = 100
            self.on_direction(config.CMD_STOP)
            self.joystick_canvas.itemconfig(self.joystick_handle, fill="#95a5a6", outline="#7f8c8d")
        
        self.joystick_canvas.coords(self.joystick_handle, 20, final_y-15, 60, final_y+15)
        self.joystick_position = position
        
    def _handle_connect(self):
        """Maneja el evento de conectar"""
        self.on_connect()
        
    def _handle_disconnect(self):
        """Maneja el evento de desconectar"""
        self.on_disconnect()
        
    def _handle_speed_change(self, speed_cmd: str):
        """Maneja el cambio de velocidad"""
        if speed_cmd == config.CMD_SPEED_HIGH:
            self.current_speed = "HIGH"
        elif speed_cmd == config.CMD_SPEED_LOW:
            self.current_speed = "LOW"
        
        self.on_speed(speed_cmd)
    
    def _on_closing(self):
        """Maneja el cierre de la ventana"""
        self.is_closed = True
        self.root.destroy()
        
    def update_connection_status(self, connected: bool):
        """Actualiza el indicador de estado de conexión"""
        if self.is_closed:
            return
            
        try:
            if connected:
                self.connection_status_label.config(
                    text="● Conectado",
                    fg="#27ae60"
                )
            else:
                self.connection_status_label.config(
                    text="● Desconectado",
                    fg="#e74c3c"
                )
        except tk.TclError:
            self.is_closed = True
            
    def update_speed_display(self, current_speed: int, max_speed: int = 255):
        """Actualiza el display de velocidad actual"""
        if self.is_closed or self.speed_display_label is None:
            return
            
        try:
            self.speed_display_label.config(text=f"{current_speed} / {max_speed}")
            
            # Cambiar color según la velocidad
            if current_speed == 0:
                color = "#e74c3c"
            elif current_speed < 128:
                color = "#f39c12"
            elif current_speed < 200:
                color = "#3498db"
            else:
                color = "#27ae60"
            
            self.speed_display_label.config(fg=color)
        except tk.TclError:
            self.is_closed = True
    
    def update_statistics(self, stats: dict):
        """Actualiza todas las estadísticas de monitoreo"""
        if self.is_closed:
            return
        
        try:
            # Latencia
            latency = stats.get("latency", {})
            avg_lat = latency.get("average", 0)
            self.stats_labels["latency"].config(text=f"{avg_lat:.1f} ms")
            
            # Confiabilidad
            reliability = stats.get("reliability", {})
            success_rate = reliability.get("success_rate", 100)
            self.stats_labels["reliability"].config(text=f"{success_rate:.1f}%")
            
            # Ancho de banda
            bandwidth = stats.get("bandwidth", {})
            total_bps = bandwidth.get("total_bps", 0)
            self.stats_labels["bandwidth"].config(text=f"{total_bps:.0f} B/s")
            
            # Comandos enviados
            commands_sent = reliability.get("commands_sent", 0)
            self.stats_labels["commands_sent"].config(text=str(commands_sent))
            
            # Pérdida de paquetes
            packet_loss = reliability.get("packet_loss", 0)
            self.stats_labels["packet_loss"].config(text=f"{packet_loss:.1f}%")
            
            # Cambiar colores según umbrales
            if avg_lat > config.LATENCY_WARNING_MS:
                self.stats_labels["latency"].config(fg="#e74c3c")
            else:
                self.stats_labels["latency"].config(fg="#27ae60")
                
            if packet_loss > config.PACKET_LOSS_WARNING:
                self.stats_labels["packet_loss"].config(fg="#e74c3c")
            else:
                self.stats_labels["packet_loss"].config(fg="#27ae60")
                
        except tk.TclError:
            self.is_closed = True
    
    def add_log_message(self, message: str):
        """Agrega un mensaje al log"""
        if self.is_closed or self.log_text is None:
            return
            
        try:
            self.log_text.config(state='normal')
            self.log_text.insert('end', message + '\n')
            self.log_text.see('end')  # Auto-scroll
            self.log_text.config(state='disabled')
        except tk.TclError:
            self.is_closed = True
            
    def clear_log(self):
        """Limpia el log de comunicación"""
        if self.is_closed or self.log_text is None:
            return
            
        try:
            self.log_text.config(state='normal')
            self.log_text.delete('1.0', 'end')
            self.log_text.config(state='disabled')
        except tk.TclError:
            self.is_closed = True
            
    def show_error(self, title: str, message: str):
        """Muestra un mensaje de error"""
        if not self.is_closed:
            try:
                messagebox.showerror(title, message)
            except tk.TclError:
                self.is_closed = True
        
    def show_info(self, title: str, message: str):
        """Muestra un mensaje informativo"""
        if not self.is_closed:
            try:
                messagebox.showinfo(title, message)
            except tk.TclError:
                self.is_closed = True
        
    def run(self):
        """Inicia el loop principal de la interfaz"""
        self.root.mainloop()
        self.is_closed = True
        
    def close(self):
        """Cierra la ventana"""
        if not self.is_closed:
            self.is_closed = True
            try:
                self.root.destroy()
            except tk.TclError:
                pass
