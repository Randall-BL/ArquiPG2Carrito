# Proyecto Control Remoto Carrito ESP32

Sistema completo de control remoto inalámbrico para un carrito robótico usando ESP32 y Python.

## 📋 Descripción del Proyecto

El proyecto consiste en el desarrollo de un carrito controlado remotamente mediante una aplicación escrita en Python, comunicada por WiFi con un microcontrolador ESP32, el cual gestiona los motores, la lectura de sensores y la transmisión de telemetría. El sistema permite desplazar el vehículo en distintas direcciones bajo control del usuario y, de manera automática, detenerse antes de una colisión gracias a la integración de un sensor ultrasónico HC-SR04 (detección de distancia frontal) y un acelerómetro MPU-6050.

Este diseño busca simular funciones de frenado autónomo y seguridad activa presentes en vehículos modernos, a la vez que fortalece el entendimiento de sistemas embebidos, control en tiempo real y comunicación inalámbrica.

### Análisis de Viabilidad Técnica

La propuesta es técnicamente viable utilizando componentes de bajo costo y alta disponibilidad, como el ESP32, sensores digitales y analógicos, motores DC con control H-Bridge y una interfaz de comunicación WiFi. El desarrollo implica tres áreas principales: control embebido, diseño de hardware y aplicación remota.

El principal desafío técnico radica en la correcta sincronización entre la lectura de sensores en tiempo real, la ejecución de rutinas de control y la transmisión de datos hacia la aplicación Python sin generar latencias perceptibles y con bajo consumo energetico. En términos de complejidad, el proyecto se considera de nivel medio-alto, al integrar hardware, software y comunicación inalámbrica de manera simultánea.

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
│   
│
├── Esp32/                   # Código para ESP32
│   ├── Esp32.ino           # Programa principal ESP32
├── docs/                   # Código para ESP32
│   ├── Readme.md           #La misma documentación que en al Raiz
│   ├── Documentación_diseño.md         # Documentación del diseño del proyecto
│   
│  
└── README.md               # Documentación en Raiz
```

## 🚀 Características Principales

### Aplicación Python
- ✅ Interfaz gráfica intuitiva con Tkinter
- ✅ D-Pad virtual para control de dirección
- ✅ Control de velocidad (multiples niveles)
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
- ✅ Multiples niveles de velocidad
- ✅ **Sensor ultrasónico HC-SR04 (detección de distancia)**
- ✅ **Acelerómetro MPU-6050 (detección de impactos)**
- ✅ **Parada automática ante colisiones**
- ✅ **Transmisión de telemetría**
- ✅ Indicadores LED

## 🛠️ Hardware Necesario

| Componente | Cantidad | Descripción | Precio Estándar |
|------------|----------|-------------|-----------------|
| ESP32 | 1 | Microcontrolador WiFi | $8 - $12 USD |
| L298N | 1 | Puente H para motores DC | $2 - $3 USD |
| Motores DC | 2 | Motor 6-12V con eje | $3 - $5 USD c/u |
| Batería | 1 | Batería 6-12V (LiPo o Pb-ácido) | $10 - $25 USD |
| **Sensor Ultrasónico HC-SR04** | 1 | Sensor de distancia | $2 - $4 USD |
| **Acelerómetro MPU-6050** | 1 | Sensor IMU (acelerómetro + giroscopio) | $3 - $5 USD |
| Cables Jumper | 40 piezas | Macho-macho | $1 - $2 USD |
| Chasis de Carrito | 1 | Base de plástico para carrito | $5 - $8 USD |
| Ruedas | 2-4 | Ruedas según diseño (incluidas en chasis frecuentemente) | $3 - $6 USD |
| Powerbank | 1 | 5V para ESP32 (opcional) | $10 - $15 USD |
| **Condensadores** | 2 | 100µF para filtrado | $1 USD |
| Placa Perforada | 1 | Para conexiones | $2 - $4 USD |
| **Costo Total Aproximado** | - | - | **$50 - $100 USD** |

## 📋 Requisitos de Software

### Para Python (PC)
- Python 3.7+
- Tkinter (incluido con Python)
- Socket (biblioteca estándar)

### Para ESP32
- Arduino IDE 1.8+ o 2.x
- ESP32 Board Support
- Ninguna biblioteca adicional requerida

## 🎯 Guía de Inicio Rápido

### 1. Configurar el Hardware

1. Conecta los motores al L298N
2. Conecta el L298N al ESP32 según el diagrama
3. Conecta el sensor HC-SR04 al GPIO 35 (TRIG) y GPIO 32 (ECHO)
4. Conecta el acelerómetro MPU-6050 vía I2C (GPIO 21 SDA, GPIO 22 SCL)
5. Alimenta el ESP32 y los motores
6. Sube el código al ESP32

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

### Configurar Distancia de Detección

En `Esp32/carrito_control.ino`:
```cpp
#define DISTANCE_THRESHOLD 20  // cm - distancia mínima para detener
```
-

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
└─────────────────┘                        │        │        │
                                            │  ┌─────▼──────┐ │
                                            │  │  Sensores  │ │
                                            │  │ HC-SR04    │ │
                                            │  │ MPU-6050   │ │
                                            │  └────────────┘ │
                                            └────────┼─────────┘
                                                    │
                                            ┌───────▼────────┐
                                            │  Motores DC    │
                                            └────────────────┘
```

## 📊 Diagrama de Conexión

```
              ESP32
                   |
    +--------------+---------------+
    |              |               |
   GPIO25        GPIO26          GPIO32
    |              |               |
    IN1           IN2             ENA
    |              |               |
    +---------- L298N ------------+
    |              |               |
    IN3           IN4             ENB
    |              |               |
   GPIO27        GPIO14          GPIO33
    |              |               |
    +--------------+---------------+
                   |
              Motor Izq & Der
                   |
              Batería 6-12V
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
| ESP32 → PC | `COLLISION\n` | - | Colisión detectada |
| ESP32 → PC | `DISTANCE:XX\n` | XX (cm) | Distancia frontal |
| ESP32 → PC | `ACCEL:X,Y,Z\n` | Valores | Datos acelerómetro |

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

### El sensor HC-SR04 no funciona

1. ✅ Verifica conexiones (TRIG, ECHO, GND, VCC)
2. ✅ Asegúrate de que haya objetos frente al sensor
3. ✅ Prueba en el Monitor Serie

### El MPU-6050 no se detecta

1. ✅ Verifica las conexiones I2C (SDA GPIO 21, SCL GPIO 22)
2. ✅ Usa resistencias pull-up si es necesario
3. ✅ Verifica la dirección I2C (0x68)

### La interfaz Python no abre

1. ✅ Verifica que Python 3.7+ esté instalado
2. ✅ Asegúrate de tener Tkinter instalado
3. ✅ Ejecuta desde la carpeta Aplicacion/

## 🔄 Extensiones Futuras

### Software
- [ ] Control de velocidad con slider continuo
- [ ] Soporte para gamepad/joystick USB
- [ ] Telemetría avanzada (batería, distancia, aceleración)
- [ ] Grabación y reproducción de trayectorias
- [ ] Streaming de cámara
- [ ] Modo autónomo con mapeo de obstáculos
- [ ] Dashboard web para monitoreo remoto

### Hardware
- [ ] Módulo de cámara ESP32-CAM
- [ ] Sensor de velocidad (encoders)
- [ ] Luces LED direccionales RGB
- [ ] Buzzer para señales audibles
- [ ] Sensor de nivel de batería
- [ ] Módulo GPS para localización

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
│                                 │
│  Monitoreo en Tiempo Real       │
│  Distancia: 45 cm │
│  Aceleración: 0.2g              │
└─────────────────────────────────┘
```



##  Licencia

Proyecto educativo para el curso de Arquitectura de Computadores.
Libre para uso académico.

