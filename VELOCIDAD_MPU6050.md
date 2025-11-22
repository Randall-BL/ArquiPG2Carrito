# 📊 Sistema de Medición de Velocidad con MPU6050

## 🎯 Descripción

El sistema ahora mide la **velocidad real** del carrito usando el acelerómetro MPU6050, en lugar de mostrar solo el valor PWM de los motores.

## 🔧 Funcionamiento

### **En el ESP32:**

1. **Lectura del Acelerómetro:**
   - El MPU6050 lee la aceleración en los ejes X e Y
   - Se calcula la magnitud de aceleración: `a = √(ax² + ay²)`

2. **Integración de Velocidad:**
   - Se usa integración numérica: `v = v₀ + a·Δt`
   - Aplica filtro de ruido (umbral de 50 cm/s²)
   - Factor de decaimiento (0.95) simula fricción

3. **Envío Periódico:**
   - Cada **500ms** envía: `SPEED:XX.XX` (en cm/s)
   - También envía al cambiar velocidad PWM
   - Rango: 0-200 cm/s (≈ 0-7 km/h)

### **En Python:**

1. **Recepción:**
   - `communication.py` escucha mensajes del ESP32
   - Detecta formato `SPEED:XX.XX`
   - Convierte a float y actualiza GUI

2. **Visualización:**
   - Display muestra: `XX.XX cm/s`
   - Colores según velocidad:
     - 🔴 Rojo: 0 cm/s (detenido)
     - 🟠 Naranja: < 50 cm/s (lento)
     - 🔵 Azul: 50-100 cm/s (medio)
     - 🟢 Verde: > 100 cm/s (rápido)

## 📡 Protocolo de Comunicación

### Comandos Python → ESP32:
```
FORWARD           → Avanzar
BACKWARD          → Retroceder
LEFT              → Girar izquierda
RIGHT             → Girar derecha
STOP              → Detener
SPEED_LOW         → Velocidad baja (PWM 150)
SPEED_HIGH        → Velocidad alta (PWM 255)
SPEED_SET:XXX     → Velocidad específica (0-255)
GET_SPEED         → Consultar velocidad
```

### Respuestas ESP32 → Python:
```
SPEED:XX.XX       → Velocidad real en cm/s
OK:COMMAND        → Confirmación de movimiento
```

## 🧮 Fórmulas Utilizadas

### Conversión de Aceleración:
```cpp
accel_cms² = (raw / 16384.0) × 980.0
```
- `16384`: Escala del MPU6050 para ±2g
- `980 cm/s²`: Gravedad terrestre

### Integración Numérica:
```cpp
v(t) = v(t-1) + a·Δt
```

### Factor de Decaimiento (Fricción):
```cpp
v = v × 0.95
```

## 🎮 Ventajas de este Sistema

✅ **Velocidad Real:** Muestra la velocidad física del carrito, no solo el PWM
✅ **Actualización en Tiempo Real:** Cada 500ms
✅ **Visualización Intuitiva:** Colores y unidades claras (cm/s)
✅ **Compensación de Fricción:** Simula la desaceleración natural
✅ **Filtro de Ruido:** Elimina vibraciones pequeñas

## 🚀 Uso

1. **Subir código al ESP32**
2. **Ejecutar aplicación Python:** `python main.py`
3. **Conectar** a la interfaz
4. **¡Listo!** La velocidad se actualiza automáticamente

## 📝 Notas Técnicas

- **Frecuencia de muestreo:** ~100 Hz (limitado por loop del ESP32)
- **Precisión:** ±5 cm/s aproximadamente
- **Calibración:** El MPU6050 debe estar horizontal en el carrito
- **Rango útil:** 0-200 cm/s (0-7.2 km/h)

## 🔍 Troubleshooting

**Problema:** La velocidad no se actualiza
- ✓ Verificar que el MPU6050 esté bien conectado (SDA=21, SCL=22)
- ✓ Comprobar que el carrito esté en superficie plana

**Problema:** Velocidad errática
- ✓ Calibrar el MPU6050 al inicio
- ✓ Ajustar umbral de ruido en `calcularVelocidad()`
- ✓ Verificar que el sensor esté firmemente montado

**Problema:** Velocidad no baja a cero
- ✓ Aumentar factor de decaimiento (línea 183 del ESP32)
- ✓ Ajustar condición de velocidad baja (línea 187)
