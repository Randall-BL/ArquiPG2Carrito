# Proyecto Control Remoto Carrito ESP32

Sistema completo de control remoto inalámbrico para un carrito robótico usando ESP32 y Python.

## 📁 Estructura del Proyecto

```
ArquiPG2Carrito/
├── Aplicacion/              # Aplicación Python (Control Remoto)
│   ├── main.py             # Punto de entrada
│   ├── controller.py       # Controlador principal
│   ├── gui.py              # Interfaz gráfica
│   ├── communication.py    # Comunicación WiFi
│   ├── monitoring.py       # Sistema de monitoreo
│   ├── notifications.py    # Notificaciones SMS (Twilio)
│   ├── config.py           # Configuración
│   ├── requirements.txt    # Dependencias
│   ├── test_twilio.py      # Prueba de SMS
│   ├── CONFIGURAR_TWILIO.md # Guía de Twilio
│   └── README.md           # Documentación Python
│
├── Esp32/                   # Código para ESP32
│   ├── Esp32.ino           # Programa principal ESP32
│   └── README.md           # Documentación ESP32
│
├── SISTEMA_COLISION.md     # Documentación de colisiones
└── README.md               # Este archivo
```

## 🚀 Características Principales

### Aplicación Python
- ✅ Interfaz gráfica intuitiva con Tkinter
- ✅ D-Pad virtual para control de dirección
- ✅ Control de velocidad (2 niveles)
- ✅ Atajos de teclado
- ✅ Comunicación WiFi TCP/IP
- ✅ **Panel de monitoreo en tiempo real**
- ✅ **Sistema de detección de colisión**
- ✅ **Notificaciones SMS automáticas (Twilio)**
- ✅ Arquitectura modular

### ESP32
- ✅ Access Point WiFi
- ✅ Servidor TCP en puerto 80
- ✅ Control PWM de motores
- ✅ Soporte para puente H (L298N)
- ✅ 2 niveles de velocidad
- ✅ **Sensor de colisión (GPIO 34)**
- ✅ **Parada automática ante colisiones**
- ✅ Indicadores LED

## 🛠️ Hardware Necesario

| Componente | Cantidad | Descripción |
|------------|----------|-------------|
| ESP32 | 1 | Cualquier modelo |
| L298N | 1 | Puente H para motores |
| Motores DC | 2 | 6-12V |
| Batería | 1 | 6-12V para motores |
| **Sensor de Colisión** | 1 | Táctil, bumper o HC-SR04 (opcional) |
| Cables jumper | - | Para conexiones |
| Chasis | 1 | Base del carrito |
| Powerbank | 1 | 5V para ESP32 (opcional) |
| Cables | varios | Jumpers macho-macho |
| Chasis | 1 | Para el carrito |
| Ruedas | 2-4 | Según diseño |

## 📋 Requisitos de Software

### Para Python (PC)
- Python 3.7+
- Tkinter (incluido con Python)
- Socket (biblioteca estándar)

### Para ESP32
- Arduino IDE 1.8+ o 2.x
- ESP32 Board Support
- Ninguna biblioteca adicional

## 🎯 Guía de Inicio Rápido

### 1. Configurar el Hardware

1. Conecta los motores al L298N
2. Conecta el L298N al ESP32 según el diagrama
3. Alimenta el ESP32 y los motores
4. Sube el código al ESP32

Ver [Esp32/README.md](Esp32/README.md) para detalles de conexión.

### 2. Configurar el ESP32

1. Abre `Esp32/carrito_control.ino` en Arduino IDE
2. Ajusta pines si es necesario
3. Carga el código al ESP32
4. Verifica en el Monitor Serie que inicie correctamente

### 3. Ejecutar la Aplicación Python

1. Navega a la carpeta `Aplicacion/`
2. Ejecuta:
   ```bash
   python main.py
   ```
3. Conecta tu PC a la red WiFi "ESP32_Carrito"
4. Haz clic en "Conectar" en la interfaz
5. ¡Controla tu carrito!

## 🎮 Controles

### Interfaz Gráfica
- **▲** - Avanzar
- **▼** - Retroceder
- **◄** - Girar izquierda
- **►** - Girar derecha
- **■** - Detener
- **🐌 BAJA** - Velocidad baja
- **🚀 ALTA** - Velocidad alta

### Teclado
- **Flechas** - Dirección
- **Espacio** - Detener
- **1** - Velocidad baja
- **2** - Velocidad alta

## 🔧 Configuración

### Cambiar IP/Puerto del ESP32

En `Aplicacion/config.py`:
```python
ESP32_IP = "192.168.4.1"
ESP32_PORT = 80
```

### Cambiar Credenciales WiFi

En `Esp32/carrito_control.ino`:
```cpp
const char* ssid = "ESP32_Carrito";
const char* password = "12345678";
```

### Ajustar Velocidades

En `Aplicacion/config.py`:
```python
SPEED_LOW = 150   # PWM 0-255
SPEED_HIGH = 255
```

### 🚨 Configurar Notificaciones SMS (Opcional)

Para recibir alertas de colisión por SMS:

1. **Crear cuenta en Twilio** (gratis, $15 USD crédito)
   - https://www.twilio.com/try-twilio

2. **Configurar credenciales** en `config.py`:
```python
TWILIO_ACCOUNT_SID = "tu_account_sid"
TWILIO_AUTH_TOKEN = "tu_auth_token"
TWILIO_PHONE_FROM = "+1234567890"  # Tu número Twilio
TWILIO_PHONE_TO = "+50662494299"    # Número destino
```

3. **Probar configuración**:
```bash
python test_twilio.py
```

📚 **Guía completa**: Ver `Aplicacion/CONFIGURAR_TWILIO.md` y `SISTEMA_COLISION.md`

## 📡 Arquitectura del Sistema

```
┌─────────────────┐          WiFi          ┌─────────────────┐
│   PC (Python)   │◄─────────────────────►│     ESP32       │
│                 │      TCP Socket        │                 │
│  ┌───────────┐  │                        │  ┌───────────┐  │
│  │    GUI    │  │                        │  │  WiFi AP  │  │
│  └─────┬─────┘  │                        │  └─────┬─────┘  │
│        │        │                        │        │        │
│  ┌─────▼─────┐  │                        │  ┌─────▼─────┐  │
│  │Controller │  │                        │  │  Control  │  │
│  └─────┬─────┘  │                        │  │  Motores  │  │
│        │        │                        │  └─────┬─────┘  │
│  ┌─────▼─────┐  │                        │        │        │
│  │   Comm    │  │    Comandos String     │  ┌─────▼─────┐  │
│  │  Module   │──┼───────────────────────►│  │   PWM     │  │
│  └───────────┘  │    FORWARD, STOP, etc  │  └─────┬─────┘  │
└─────────────────┘                        └────────┼─────────┘
                                                    │
                                            ┌───────▼────────┐
                                            │  Motores DC    │
                                            └────────────────┘
```

## 📊 Protocolo de Comunicación

| Dirección | Comando | Payload | Descripción |
|-----------|---------|---------|-------------|
| PC → ESP32 | `FORWARD\n` | - | Avanzar |
| PC → ESP32 | `BACKWARD\n` | - | Retroceder |
| PC → ESP32 | `LEFT\n` | - | Girar izquierda |
| PC → ESP32 | `RIGHT\n` | - | Girar derecha |
| PC → ESP32 | `STOP\n` | - | Detener |
| PC → ESP32 | `SPEED_LOW\n` | - | Vel. baja (150) |
| PC → ESP32 | `SPEED_HIGH\n` | - | Vel. alta (255) |
| ESP32 → PC | `OK\n` | - | Confirmación |

## 🐛 Solución de Problemas

### No puedo conectarme al ESP32

1. ✅ Verifica que el ESP32 esté encendido
2. ✅ Busca la red "ESP32_Carrito" en tu PC
3. ✅ Conéctate con contraseña "12345678"
4. ✅ Verifica que la IP sea 192.168.4.1
5. ✅ Desactiva el firewall temporalmente

### Los motores no responden

1. ✅ Verifica las conexiones del L298N
2. ✅ Comprueba la alimentación
3. ✅ Verifica que GND esté compartido
4. ✅ Revisa los pines en el código
5. ✅ Prueba con velocidad alta primero

### La interfaz Python no abre

1. ✅ Verifica que Python 3.7+ esté instalado
2. ✅ Asegúrate de tener Tkinter instalado
3. ✅ Ejecuta desde la carpeta Aplicacion/

## 🔄 Extensiones Futuras

### Software
- [ ] Control de velocidad con slider continuo
- [ ] Soporte para gamepad/joystick USB
- [ ] Telemetría en tiempo real (batería, distancia)
- [ ] Grabación y reproducción de trayectorias
- [ ] Streaming de cámara
- [ ] Modo autónomo (evitar obstáculos)

### Hardware
- [ ] Sensor ultrasónico HC-SR04
- [ ] Módulo de cámara ESP32-CAM
- [ ] Sensor de velocidad (encoders)
- [ ] Luces LED direccionales
- [ ] Buzzer para señales

## 📸 Capturas de Pantalla

### Interfaz Python
```
┌─────────────────────────────────┐
│   🚗 Control Remoto ESP32       │
│                                 │
│   ● Conectado                   │
│  ┌──────────┬──────────┐       │
│  │ Conectar │Desconectar│       │
│  └──────────┴──────────┘       │
│  ─────────────────────────      │
│         Dirección               │
│          ▲                      │
│       ◄  ■  ►                   │
│          ▼                      │
│  ─────────────────────────      │
│        Velocidad                │
│  ┌─────────┐  ┌────────┐       │
│  │🐌 BAJA  │  │🚀 ALTA │       │
│  └─────────┘  └────────┘       │
└─────────────────────────────────┘
```

## 👥 Contribuciones

Este es un proyecto educativo. Si encuentras mejoras o bugs:
1. Crea un issue
2. Haz un fork
3. Envía un pull request

## 📄 Licencia

Proyecto educativo para el curso de Arquitectura de Computadores.
Libre para uso académico.

## 📞 Contacto

Para dudas o sugerencias sobre el proyecto, consulta con tu instructor o crea un issue en el repositorio.

---

**¡Disfruta construyendo tu carrito controlado por ESP32!** 🚗💨
