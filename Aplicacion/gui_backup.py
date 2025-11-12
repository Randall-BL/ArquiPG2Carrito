"""
Módulo de interfaz gráfica del control remoto
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable
import config


class ControlGUI:
    """Clase para la interfaz gráfica del control remoto"""
    
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
        self.speed_display_label = None  # Display para mostrar velocidad actual
        self.is_closed = False  # Flag para verificar si la ventana está cerrada
        
        # Referencias para el panel de monitoreo
        self.latency_label = None
        self.bandwidth_label = None
        self.reliability_label = None
        self.log_text = None
        self.stats_labels = {}
        
        # Manejar el cierre de la ventana
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self._setup_ui()
        self._setup_key_bindings()
        
    def _setup_ui(self):
        """Configura todos los elementos de la interfaz"""
        # Frame contenedor principal con dos columnas
        container = tk.Frame(self.root, bg=config.BACKGROUND_COLOR)
        container.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Columna izquierda: Controles
        left_frame = tk.Frame(container, bg=config.BACKGROUND_COLOR)
        left_frame.pack(side='left', fill='both', expand=False, padx=(0, 10))
        
        # Columna derecha: Monitoreo
        right_frame = tk.Frame(container, bg=config.BACKGROUND_COLOR, relief='solid', borderwidth=1)
        right_frame.pack(side='right', fill='both', expand=True)
        
        self._setup_control_panel(left_frame)
        self._setup_monitoring_panel(right_frame)
        
    def _setup_control_panel(self, parent):
        """Configura el panel de controles"""
        
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
        title.pack(pady=(0, 10))
        
        # Estado de conexión
        self.connection_status_label = tk.Label(
            parent,
            text="● Desconectado",
            font=("Arial", 10),
            bg=config.BACKGROUND_COLOR,
            fg="#e74c3c"
        )
        self.connection_status_label.pack(pady=5)
        
        # Botones de conexión
        conn_frame = tk.Frame(parent, bg=config.BACKGROUND_COLOR)
        conn_frame.pack(pady=10)
        
        connect_btn = tk.Button(
            conn_frame,
            text="Conectar",
            font=("Arial", 10),
            bg="#27ae60",
            fg="white",
            width=12,
            height=1,
            command=self._handle_connect
        )
        connect_btn.pack(side='left', padx=5)
        
        disconnect_btn = tk.Button(
            conn_frame,
            text="Desconectar",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            width=12,
            height=1,
            command=self._handle_disconnect
        )
        disconnect_btn.pack(side='left', padx=5)
        
        # Separador
        separator1 = tk.Frame(parent, height=2, bg="#34495e")
        separator1.pack(fill='x', pady=15)
        
        # D-Pad de dirección
        dpad_label = tk.Label(
            parent,
            text="Dirección",
            font=("Arial", 12, "bold"),
            bg=config.BACKGROUND_COLOR,
            fg="white"
        )
        dpad_label.pack(pady=(0, 10))
        
        self._create_dpad(parent)
        
        # Separador
        separator2 = tk.Frame(parent, height=2, bg="#34495e")
        separator2.pack(fill='x', pady=15)
        
        # Controles de velocidad
        speed_label = tk.Label(
            parent,
            text="Velocidad",
            font=("Arial", 12, "bold"),
            bg=config.BACKGROUND_COLOR,
            fg="white"
        )
        speed_label.pack(pady=(0, 10))
        
        self._create_speed_controls(parent)
        
        # Instrucciones
        instructions = tk.Label(
            parent,
            text="Usa las flechas del teclado o los botones\n1=Baja | 2=Alta | +/- = Subir/Bajar",
            font=("Arial", 8),
            bg=config.BACKGROUND_COLOR,
            fg="#95a5a6"
        )
        instructions.pack(side='bottom', pady=(10, 0))
        
    def _create_dpad(self, parent):
        """Crea el D-Pad de dirección"""
        dpad_frame = tk.Frame(parent, bg=config.BACKGROUND_COLOR)
        dpad_frame.pack(pady=10)
        
        # Arriba
        btn_up = tk.Button(
            dpad_frame,
            text="▲",
            font=("Arial", 16, "bold"),
            bg=config.BUTTON_COLOR,
            fg=config.BUTTON_TEXT_COLOR,
            activebackground=config.BUTTON_ACTIVE_COLOR,
            width=5,
            height=2
        )
        btn_up.grid(row=0, column=1, padx=2, pady=2)
        btn_up.bind('<ButtonPress-1>', lambda e: self.on_direction(config.CMD_FORWARD))
        btn_up.bind('<ButtonRelease-1>', lambda e: self.on_direction(config.CMD_STOP))
        
        # Izquierda
        btn_left = tk.Button(
            dpad_frame,
            text="◄",
            font=("Arial", 16, "bold"),
            bg=config.BUTTON_COLOR,
            fg=config.BUTTON_TEXT_COLOR,
            activebackground=config.BUTTON_ACTIVE_COLOR,
            width=5,
            height=2
        )
        btn_left.grid(row=1, column=0, padx=2, pady=2)
        btn_left.bind('<ButtonPress-1>', lambda e: self.on_direction(config.CMD_LEFT))
        btn_left.bind('<ButtonRelease-1>', lambda e: self.on_direction(config.CMD_STOP))
        
        # Centro (Stop)
        btn_stop = tk.Button(
            dpad_frame,
            text="■",
            font=("Arial", 16, "bold"),
            bg="#e74c3c",
            fg=config.BUTTON_TEXT_COLOR,
            activebackground="#c0392b",
            width=5,
            height=2,
            command=lambda: self.on_direction(config.CMD_STOP)
        )
        btn_stop.grid(row=1, column=1, padx=2, pady=2)
        
        # Derecha
        btn_right = tk.Button(
            dpad_frame,
            text="►",
            font=("Arial", 16, "bold"),
            bg=config.BUTTON_COLOR,
            fg=config.BUTTON_TEXT_COLOR,
            activebackground=config.BUTTON_ACTIVE_COLOR,
            width=5,
            height=2
        )
        btn_right.grid(row=1, column=2, padx=2, pady=2)
        btn_right.bind('<ButtonPress-1>', lambda e: self.on_direction(config.CMD_RIGHT))
        btn_right.bind('<ButtonRelease-1>', lambda e: self.on_direction(config.CMD_STOP))
        
        # Abajo
        btn_down = tk.Button(
            dpad_frame,
            text="▼",
            font=("Arial", 16, "bold"),
            bg=config.BUTTON_COLOR,
            fg=config.BUTTON_TEXT_COLOR,
            activebackground=config.BUTTON_ACTIVE_COLOR,
            width=5,
            height=2
        )
        btn_down.grid(row=2, column=1, padx=2, pady=2)
        btn_down.bind('<ButtonPress-1>', lambda e: self.on_direction(config.CMD_BACKWARD))
        btn_down.bind('<ButtonRelease-1>', lambda e: self.on_direction(config.CMD_STOP))
        
    def _create_speed_controls(self, parent):
        """Crea los controles de velocidad"""
        speed_frame = tk.Frame(parent, bg=config.BACKGROUND_COLOR)
        speed_frame.pack(pady=10)
        
        # Frame superior: botones preestablecidos
        preset_frame = tk.Frame(speed_frame, bg=config.BACKGROUND_COLOR)
        preset_frame.pack(pady=5)
        
        # Velocidad Baja
        btn_speed_low = tk.Button(
            preset_frame,
            text="🐌 BAJA",
            font=("Arial", 10, "bold"),
            bg="#f39c12",
            fg="white",
            activebackground="#e67e22",
            width=10,
            height=2,
            command=lambda: self._handle_speed_change(config.CMD_SPEED_LOW)
        )
        btn_speed_low.pack(side='left', padx=5)
        
        # Velocidad Alta
        btn_speed_high = tk.Button(
            preset_frame,
            text="🚀 ALTA",
            font=("Arial", 10, "bold"),
            bg="#e74c3c",
            fg="white",
            activebackground="#c0392b",
            width=10,
            height=2,
            command=lambda: self._handle_speed_change(config.CMD_SPEED_HIGH)
        )
        btn_speed_high.pack(side='left', padx=5)
        
        # Display de velocidad actual
        display_frame = tk.Frame(speed_frame, bg=config.BACKGROUND_COLOR)
        display_frame.pack(pady=10)
        
        tk.Label(
            display_frame,
            text="Velocidad Actual:",
            font=("Arial", 10),
            bg=config.BACKGROUND_COLOR,
            fg="white"
        ).pack()
        
        self.speed_display_label = tk.Label(
            display_frame,
            text="150 / 255",
            font=("Arial", 16, "bold"),
            bg="#34495e",
            fg="#3498db",
            width=12,
            relief="sunken",
            padx=10,
            pady=5
        )
        self.speed_display_label.pack(pady=5)
        
        # Frame inferior: botones de incremento/decremento
        adjust_frame = tk.Frame(speed_frame, bg=config.BACKGROUND_COLOR)
        adjust_frame.pack(pady=5)
        
        # Botón decrementar
        btn_speed_down = tk.Button(
            adjust_frame,
            text="▼ BAJAR",
            font=("Arial", 10, "bold"),
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            width=10,
            height=2,
            command=lambda: self._handle_speed_change(config.CMD_SPEED_DOWN)
        )
        btn_speed_down.pack(side='left', padx=5)
        
        # Botón incrementar
        btn_speed_up = tk.Button(
            adjust_frame,
            text="▲ SUBIR",
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#229954",
            width=10,
            height=2,
            command=lambda: self._handle_speed_change(config.CMD_SPEED_UP)
        )
        btn_speed_up.pack(side='left', padx=5)
        
    def _setup_key_bindings(self):
        """Configura los atajos de teclado"""
        # Direcciones
        self.root.bind('<Up>', lambda e: self.on_direction(config.CMD_FORWARD))
        self.root.bind('<Down>', lambda e: self.on_direction(config.CMD_BACKWARD))
        self.root.bind('<Left>', lambda e: self.on_direction(config.CMD_LEFT))
        self.root.bind('<Right>', lambda e: self.on_direction(config.CMD_RIGHT))
        self.root.bind('<KeyRelease-Up>', lambda e: self.on_direction(config.CMD_STOP))
        self.root.bind('<KeyRelease-Down>', lambda e: self.on_direction(config.CMD_STOP))
        self.root.bind('<KeyRelease-Left>', lambda e: self.on_direction(config.CMD_STOP))
        self.root.bind('<KeyRelease-Right>', lambda e: self.on_direction(config.CMD_STOP))
        self.root.bind('<space>', lambda e: self.on_direction(config.CMD_STOP))
        
        # Velocidades
        self.root.bind('1', lambda e: self._handle_speed_change(config.CMD_SPEED_LOW))
        self.root.bind('2', lambda e: self._handle_speed_change(config.CMD_SPEED_HIGH))
        self.root.bind('+', lambda e: self._handle_speed_change(config.CMD_SPEED_UP))
        self.root.bind('=', lambda e: self._handle_speed_change(config.CMD_SPEED_UP))  # Para teclados sin numpad
        self.root.bind('-', lambda e: self._handle_speed_change(config.CMD_SPEED_DOWN))
        
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
        # Para CMD_SPEED_UP y CMD_SPEED_DOWN, el controller manejará el valor
        
        self.on_speed(speed_cmd)
    
    def update_speed_display(self, current_speed: int, max_speed: int = 255):
        """Actualiza el display de velocidad actual"""
        if self.is_closed or self.speed_display_label is None:
            return
            
        try:
            self.speed_display_label.config(
                text=f"{current_speed} / {max_speed}"
            )
            
            # Cambiar color según la velocidad
            if current_speed == 0:
                color = "#e74c3c"  # Rojo si está detenido
            elif current_speed < 128:
                color = "#f39c12"  # Naranja para velocidad baja
            elif current_speed < 200:
                color = "#3498db"  # Azul para velocidad media
            else:
                color = "#27ae60"  # Verde para velocidad alta
            
            self.speed_display_label.config(fg=color)
        except tk.TclError:
            self.is_closed = True
    
    def _on_closing(self):
        """Maneja el cierre de la ventana"""
        self.is_closed = True
        self.root.destroy()
        
    def update_connection_status(self, connected: bool):
        """Actualiza el indicador de estado de conexión"""
        if self.is_closed:
            return  # No intentar actualizar si la ventana está cerrada
            
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
            # La ventana ya fue destruida
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
        self.is_closed = True  # Marcar como cerrado cuando el mainloop termine
        
    def close(self):
        """Cierra la ventana"""
        if not self.is_closed:
            self.is_closed = True
            try:
                self.root.destroy()
            except tk.TclError:
                pass  # Ya fue destruida
