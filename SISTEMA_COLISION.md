# 🚨 Sistema de Detección de Colisión con Notificaciones SMS

## 📋 Resumen

Este sistema detecta colisiones en el carrito ESP32 y envía notificaciones por SMS automáticamente usando Twilio.

## 🔧 Componentes Implementados

### 1. **Hardware (ESP32)**
- **Sensor de colisión** en el pin 34
- **Detección automática** de impactos
- **Parada inmediata** de motores
- **Envío de alerta** al cliente Python

### 2. **Software (Python)**
- **Módulo de notificaciones** (`notifications.py`)
- **Integración con Twilio** para SMS
- **Detección de mensajes** del ESP32
- **Sistema de cooldown** para evitar spam

### 3. **Interfaz (GUI)**
- **Alertas visuales** en el log
- **Notificaciones emergentes**
- **Registro de eventos**

## 🔌 Conexiones del Hardware

### Sensor de Colisión (Recomendado)

**Opción A: Sensor Táctil / Bumper**
```
Sensor     →  ESP32
─────────────────────
VCC        →  3.3V
GND        →  GND
OUT        →  GPIO 34
```

**Opción B: Sensor Ultrasónico HC-SR04**
```
HC-SR04    →  ESP32
─────────────────────
VCC        →  5V
GND        →  GND
TRIG       →  GPIO 33
ECHO       →  GPIO 34
```

**Opción C: Simulación (Para Pruebas)**
- Conecta un botón pulsador entre GPIO 34 y GND
- El pin 34 tiene pull-up interno activado
- Al presionar el botón = colisión detectada

## ⚙️ Configuración Paso a Paso

### Paso 1: Instalar Dependencias

```bash
cd Aplicacion
pip install -r requirements.txt
```

### Paso 2: Configurar Twilio

1. **Crear cuenta en Twilio** (gratis, $15 USD de crédito)
   - https://www.twilio.com/try-twilio

2. **Obtener credenciales**
   - Dashboard: https://console.twilio.com
   - Copia: Account SID y Auth Token

3. **Verificar número de destino** (+50662494299)
   - https://console.twilio.com/us1/develop/phone-numbers/manage/verified
   - Sigue el proceso de verificación

4. **Configurar en `config.py`**
```python
# Configuración de Twilio (SMS)
TWILIO_ACCOUNT_SID = "ACxxxxxxxx..."  # Tu Account SID
TWILIO_AUTH_TOKEN = "tu_token..."      # Tu Auth Token
TWILIO_PHONE_FROM = "+1234567890"     # Tu número Twilio
TWILIO_PHONE_TO = "+50662494299"      # Número verificado
```

### Paso 3: Probar Configuración

```bash
python test_twilio.py
```

Esto verificará:
- ✅ Credenciales correctas
- ✅ Conexión con Twilio
- ✅ Envío de SMS de prueba (opcional)

### Paso 4: Cargar Código al ESP32

1. Abre `Esp32/Esp32.ino` en Arduino IDE
2. Verifica el pin del sensor (GPIO 34)
3. Carga el código al ESP32

### Paso 5: Ejecutar Aplicación

```bash
python main.py
```

## 🎯 Cómo Funciona

### Flujo de Detección

```
1. Sensor detecta colisión
   ↓
2. ESP32 detiene motores
   ↓
3. ESP32 envía "COLISION_DETECTADA"
   ↓
4. Python recibe el mensaje
   ↓
5. Python detiene carrito (doble seguridad)
   ↓
6. Python envía SMS vía Twilio
   ↓
7. Usuario recibe alerta en +50662494299
```

### Mensaje SMS Recibido

```
🚨 ALERTA DE COLISIÓN 🚨

El carrito ESP32 ha detectado una colisión.
El sistema se ha detenido automáticamente.

Hora: 14:35:22
Fecha: 14/11/2025
```

## 🔒 Seguridad y Límites

### Cooldown de Notificaciones
- **10 segundos** entre SMS (configurable)
- Evita spam y ahorra créditos
- Configurable en `config.py`:
```python
COLLISION_COOLDOWN = 10  # Segundos
```

### Debounce del Sensor
- **1 segundo** entre detecciones
- Evita falsas alarmas
- Implementado en el ESP32

## 💰 Costos

### Cuenta Trial (Gratis)
- **$15 USD de crédito**
- Solo números verificados
- Ideal para desarrollo/pruebas

### Costos por SMS a Costa Rica
- **~$0.015-0.02 USD** por mensaje
- Con $15 USD = **~750-1000 SMS**
- Más que suficiente para pruebas

### Cuenta de Producción
- Número Twilio: **~$1-2 USD/mes**
- SMS: **~$0.015 USD** c/u
- Sin límite de números destino

## 🧪 Pruebas

### Probar Sensor de Colisión

**Con botón simulado:**
1. Conecta el carrito
2. Presiona el botón en GPIO 34
3. Verifica que:
   - ✅ Carrito se detiene
   - ✅ LED parpadea
   - ✅ Mensaje en el log de Python
   - ✅ SMS recibido en +50662494299

**Con sensor real:**
1. Conecta el carrito
2. Haz que el sensor detecte un objeto
3. Verifica el mismo flujo

### Probar Solo SMS (Sin Hardware)

Crea `test_colision_manual.py`:
```python
from notifications import TwilioNotifier

notifier = TwilioNotifier()
notifier.send_collision_alert()
```

Ejecuta:
```bash
python test_colision_manual.py
```

## 📊 Monitoreo

### En la Aplicación Python
- **Log en tiempo real** de eventos
- **Contador de comandos** enviados/recibidos
- **Alertas visuales** en la GUI

### En Twilio Console
- **Estado de SMS**: https://console.twilio.com/us1/monitor/logs/sms
- **Historial completo** de mensajes
- **Costos y uso** de créditos

## 🆘 Solución de Problemas

### ❌ "No se pudo enviar SMS"

**Causa 1: Número no verificado**
- Verifica +50662494299 en Twilio Console
- Solo con cuenta Trial

**Causa 2: Credenciales incorrectas**
- Revisa Account SID y Auth Token
- Sin espacios extras

**Causa 3: Saldo insuficiente**
- Verifica tu crédito en Twilio Console
- Recarga si es necesario

### ❌ "Colisión no detectada"

**Causa 1: Sensor no conectado**
- Verifica conexión en GPIO 34
- Prueba con botón para descartar

**Causa 2: Pin incorrecto**
- Verifica que usas GPIO 34
- Cambia en código si es necesario

**Causa 3: Código no actualizado**
- Re-carga el sketch al ESP32
- Verifica que tiene las funciones de colisión

### ❌ "SMS llega tarde"

**Normal**: 5-30 segundos de retraso
- Es normal en SMS internacionales
- Twilio → operador CR → teléfono

## 📁 Archivos Modificados

```
Aplicacion/
├── config.py              ← Configuración Twilio
├── notifications.py       ← NUEVO: Sistema SMS
├── communication.py       ← Detecta mensajes de colisión
├── controller.py          ← Maneja alertas
├── requirements.txt       ← Agrega 'twilio'
├── test_twilio.py         ← NUEVO: Prueba configuración
└── CONFIGURAR_TWILIO.md   ← NUEVO: Guía completa

Esp32/
└── Esp32.ino              ← Detección de colisión
```

## 🎓 Conceptos Técnicos

### 1. **Interrupciones vs Polling**
Actualmente usa **polling** (verificación continua).
Para mayor eficiencia, podrías usar interrupciones:

```cpp
attachInterrupt(digitalPinToInterrupt(SENSOR_COLISION), 
                handleColision, FALLING);
```

### 2. **Comunicación Asíncrona**
El ESP32 envía mensajes sin esperar confirmación.
Python los captura en el hilo de comunicación.

### 3. **Rate Limiting**
Cooldown previene:
- Spam de notificaciones
- Desgaste de créditos
- Saturación del operador

## 🚀 Mejoras Futuras

### Prioridad Alta
- [ ] Múltiples sensores (frontal, trasero, laterales)
- [ ] Niveles de severidad (leve, moderado, grave)
- [ ] Log en archivo de todas las colisiones

### Prioridad Media
- [ ] Envío de ubicación GPS
- [ ] Foto/video del momento de colisión
- [ ] Notificaciones por WhatsApp (API Business)

### Prioridad Baja
- [ ] Dashboard web de monitoreo
- [ ] Estadísticas de colisiones
- [ ] Machine learning para predicción

## 📚 Referencias

- **Twilio Docs**: https://www.twilio.com/docs/sms
- **ESP32 Docs**: https://docs.espressif.com/
- **Python Twilio**: https://www.twilio.com/docs/libraries/python

## ✅ Checklist Final

Antes de usar en producción:

- [ ] Twilio configurado y probado
- [ ] Número +50662494299 verificado
- [ ] Sensor de colisión instalado
- [ ] Código ESP32 actualizado y cargado
- [ ] Prueba completa del flujo
- [ ] Cooldown configurado apropiadamente
- [ ] Créditos Twilio suficientes

---

**¡Sistema listo para detectar colisiones y enviar alertas! 🎉**
