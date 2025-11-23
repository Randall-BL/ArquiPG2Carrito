# Control Remoto Carrito ESP32

Código para ESP32 que permite controlar un carrito mediante comandos WiFi desde una aplicación Python.

## 🔌 Hardware Requerido

- **ESP32** (cualquier variante)
- **Puente H L298N** o similar (driver de motores)
- **2 Motores DC**
- **Batería** (6-12V para los motores)
- **Cables jumper**

## 📋 Conexiones

### ESP32 → L298N (Puente H)

#### Motor Izquierdo
| ESP32 Pin | L298N Pin | Función |
|-----------|-----------|---------|
| GPIO 26   | IN1       | Dirección adelante |
| GPIO 27   | IN2       | Dirección atrás |
| GPIO 14   | ENA       | Control PWM velocidad |

#### Motor Derecho
| ESP32 Pin | L298N Pin | Función |
|-----------|-----------|---------|
| GPIO 25   | IN3       | Dirección adelante |
| GPIO 33   | IN4       | Dirección atrás |
| GPIO 32   | ENB       | Control PWM velocidad |

#### Alimentación
| Conexión | Descripción |
|----------|-------------|
| L298N +12V | Batería positivo (6-12V) |
| L298N GND | GND común (ESP32 + Batería) |
| ESP32 VIN | 5V del L298N (si tiene regulador) o batería/powerbank |
| ESP32 GND | GND común |

⚠️ **IMPORTANTE**: 
- El ESP32 y el L298N deben compartir GND
- NO alimentes el ESP32 con más de 5V en VIN
- Usa una fuente separada para los motores

## 🛠️ Instalación

### 1. Instalar Arduino IDE

1. Descarga [Arduino IDE](https://www.arduino.cc/en/software)
2. Instala el IDE

### 2. Configurar ESP32 en Arduino IDE

1. Abre Arduino IDE
2. Ve a **Archivo → Preferencias**
3. En "Gestor de URLs Adicionales de Tarjetas", agrega:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Ve a **Herramientas → Placa → Gestor de tarjetas**
5. Busca "ESP32" e instala "esp32 by Espressif Systems"

### 3. Cargar el Código

1. Abre el archivo `carrito_control.ino` en Arduino IDE
2. Selecciona tu placa ESP32:
   - **Herramientas → Placa → ESP32 Arduino → ESP32 Dev Module**
3. Selecciona el puerto COM correcto:
   - **Herramientas → Puerto → COM#** (el que corresponda)
4. Haz clic en **Cargar** (→)

## ⚙️ Configuración

### Modificar Credenciales WiFi

Por defecto, el ESP32 crea una red WiFi con:
- **SSID**: `ESP32_Carrito`
- **Contraseña**: `12345678`

Para cambiar esto, edita estas líneas en el código:

```cpp
const char* ssid = "ESP32_Carrito";        // Tu nombre
const char* password = "12345678";         // Tu contraseña (min 8 chars)
```

### Ajustar Pines de Motores

Si tu conexión física es diferente, modifica estos valores:

```cpp
// Motor Izquierdo
const int MOTOR_IZQ_ADELANTE = 26;
const int MOTOR_IZQ_ATRAS = 27;
const int MOTOR_IZQ_PWM = 14;

// Motor Derecho
const int MOTOR_DER_ADELANTE = 25;
const int MOTOR_DER_ATRAS = 33;
const int MOTOR_DER_PWM = 32;
```

### Ajustar Velocidades

Modifica las velocidades predeterminadas:

```cpp
int velocidadActual = 150;  // Velocidad inicial (0-255)
```

## 🚀 Uso

### 1. Subir el código al ESP32

1. Conecta el ESP32 por USB
2. Carga el código
3. Abre el Monitor Serie (115200 baud)

### 2. Verificar la red WiFi

Deberías ver en el Monitor Serie:

```
=================================
Control Remoto Carrito ESP32
=================================

--- Configurando WiFi ---
✓ Access Point creado: ESP32_Carrito
✓ Contraseña: 12345678
✓ Dirección IP: 192.168.4.1
✓ Servidor iniciado en puerto 80

✓ Sistema listo!
Esperando conexiones...
```

### 3. Conectar desde Python

1. Conecta tu PC a la red WiFi "ESP32_Carrito"
2. Ejecuta la aplicación Python
3. Haz clic en "Conectar"

## 📡 Protocolo de Comunicación

El ESP32 recibe comandos de texto terminados en `\n`:

| Comando | Acción |
|---------|--------|
| `FORWARD` | Avanzar |
| `BACKWARD` | Retroceder |
| `LEFT` | Girar izquierda |
| `RIGHT` | Girar derecha |
| `STOP` | Detener |
| `SPEED_LOW` | Velocidad baja (150) |
| `SPEED_HIGH` | Velocidad alta (255) |

## 🔍 Depuración

### El ESP32 no aparece en Arduino IDE

- Instala drivers USB-Serial (CP210x o CH340)
- Presiona el botón BOOT mientras cargas el código
- Verifica el cable USB (algunos solo sirven para carga)

### Los motores no giran

1. Verifica las conexiones del L298N
2. Asegúrate de que los jumpers de ENA/ENB estén quitados si usas PWM
3. Verifica la alimentación de los motores
4. Comprueba que GND esté compartido

### El ESP32 se reinicia constantemente

- La fuente de alimentación puede ser insuficiente
- Los motores pueden estar consumiendo mucha corriente
- Usa una batería o powerbank de al menos 1A para el ESP32

### No puedo conectarme al WiFi

1. Verifica que el ESP32 esté encendido
2. Busca la red "ESP32_Carrito" en tu PC
3. Verifica la contraseña (12345678)
4. Asegúrate de que la IP en Python sea 192.168.4.1

## 🔧 Personalización

### Cambiar comportamiento de giros

Para giros en el lugar (un motor adelante, otro atrás):

```cpp
void motorIzquierda() {
  digitalWrite(MOTOR_IZQ_ADELANTE, LOW);
  digitalWrite(MOTOR_IZQ_ATRAS, HIGH);  // Izq atrás
  digitalWrite(MOTOR_DER_ADELANTE, HIGH); // Der adelante
  digitalWrite(MOTOR_DER_ATRAS, LOW);
  
  ledcWrite(PWM_CHANNEL_IZQ, velocidadActual);
  ledcWrite(PWM_CHANNEL_DER, velocidadActual);
}
```

### Agregar más velocidades

Agrega más casos en `procesarComando()`:

```cpp
else if (comando == "SPEED_MEDIUM") {
  setVelocidad(200);
  Serial.println("🚗 Velocidad MEDIA");
}
```

## 📊 Diagrama de Conexión

```
                 ESP32
                   |
    +--------------+---------------+
    |              |               |
   GPIO26        GPIO27          GPIO14
    |              |               |
    IN1           IN2             ENA
    |              |               |
    +---------- L298N ------------+
    |              |               |
    IN3           IN4             ENB
    |              |               |
   GPIO25        GPIO33          GPIO32
    |              |               |
    +--------------+---------------+
                   |
              Motor Izq & Der
                   |
              Batería 6-12V
```

## 📝 Notas

- El LED integrado (GPIO 2) parpadea al conectar/desconectar
- El sistema soporta múltiples reconexiones
- La velocidad se puede cambiar en tiempo real
- Los motores se detienen automáticamente al desconectar

## 🆘 Soporte

Si tienes problemas:
1. Revisa el Monitor Serie para mensajes de error
2. Verifica todas las conexiones físicas
3. Prueba con velocidades más bajas primero
4. Asegúrate de que la alimentación sea adecuada

## 📜 Licencia

Proyecto educativo para Arquitectura de Computadores
