# Control Remoto para Carrito ESP32

Aplicación de control remoto modular en Python para controlar un carrito mediante ESP32 con comunicación WiFi.

## 🚀 Características

- **Interfaz gráfica intuitiva** con D-Pad de dirección
- **Control de velocidad** con dos niveles (Baja/Alta)
- **Comunicación WiFi** con el ESP32
- **Control por teclado** (flechas para dirección, 1/2 para velocidad)
- **Arquitectura modular** fácil de mantener y extender

## 📁 Estructura del Proyecto

```
Aplicacion/
├── main.py           # Punto de entrada principal
├── controller.py     # Controlador que coordina GUI y comunicación
├── gui.py            # Interfaz gráfica (Tkinter)
├── communication.py  # Módulo de comunicación WiFi
├── config.py         # Configuración centralizada
├── requirements.txt  # Dependencias
└── README.md         # Este archivo
```

## 🛠️ Instalación

### Requisitos
- Python 3.7 o superior
- Tkinter (incluido con Python en Windows)

### Pasos

1. Clona el repositorio o descarga los archivos

2. No se requieren dependencias adicionales (tkinter y socket vienen con Python)

## 🎮 Uso

### 1. Configurar la IP del ESP32

Edita `config.py` y ajusta la IP y puerto según tu ESP32:

```python
ESP32_IP = "192.168.4.1"  # IP de tu ESP32
ESP32_PORT = 80
```

### 2. Ejecutar la aplicación

```bash
python main.py
```

### 3. Conectar al ESP32

1. Conecta tu PC a la red WiFi del ESP32
2. Haz clic en el botón "Conectar"
3. Una vez conectado, usa los controles

## 🎯 Controles

### D-Pad (Botones o Teclado)
- **▲ / Flecha Arriba**: Avanzar
- **▼ / Flecha Abajo**: Retroceder
- **◄ / Flecha Izquierda**: Girar izquierda
- **► / Flecha Derecha**: Girar derecha
- **■ / Espacio**: Detener

### Velocidad
- **🐌 BAJA / Tecla 1**: Velocidad baja (PWM 150)
- **🚀 ALTA / Tecla 2**: Velocidad alta (PWM 255)

## 🔧 Configuración Avanzada

### Modificar velocidades

En `config.py`:

```python
SPEED_LOW = 150   # Valor PWM para velocidad baja (0-255)
SPEED_HIGH = 255  # Valor PWM para velocidad alta (0-255)
```

### Cambiar colores de la interfaz

En `config.py`:

```python
BACKGROUND_COLOR = "#2c3e50"
BUTTON_COLOR = "#3498db"
BUTTON_ACTIVE_COLOR = "#2980b9"
```

## 📡 Protocolo de Comunicación

Los comandos enviados al ESP32 son strings terminados en `\n`:

- `FORWARD\n` - Avanzar
- `BACKWARD\n` - Retroceder
- `LEFT\n` - Girar izquierda
- `RIGHT\n` - Girar derecha
- `STOP\n` - Detener
- `SPEED_LOW\n` - Velocidad baja
- `SPEED_HIGH\n` - Velocidad alta

## 🐛 Solución de Problemas

### No se puede conectar al ESP32

1. Verifica que el ESP32 esté encendido
2. Asegúrate de estar conectado a la red WiFi del ESP32
3. Verifica que la IP en `config.py` sea correcta
4. Comprueba que el firewall no bloquee la conexión

### La interfaz no responde

1. Asegúrate de estar conectado primero
2. Verifica que el ESP32 esté recibiendo los comandos
3. Revisa los mensajes en la consola

