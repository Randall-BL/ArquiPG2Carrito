# 🔧 Diagnóstico de Problemas con Giros

## ❌ Problema Reportado
Cuando presionas los botones de IZQUIERDA o DERECHA, el carrito avanza o retrocede en lugar de girar.

## ✅ Correcciones Aplicadas

### 1. **Corregida función `aplicarVelocidad()`**
```cpp
// ANTES (ERROR):
ledcWrite(ENB, 255);  // Siempre a máxima velocidad

// AHORA (CORRECTO):
ledcWrite(ENB, velocidad);  // Usa la velocidad configurada
```

### 2. **Funciones de Giro Diferencial**
Las funciones de giro ya están correctas:

```cpp
void girarDerecha() {
  // Motor Izquierdo → ADELANTE
  // Motor Derecho   → ATRÁS
  // Resultado: Gira a la DERECHA
}

void girarIzquierda() {
  // Motor Izquierdo → ATRÁS
  // Motor Derecho   → ADELANTE
  // Resultado: Gira a la IZQUIERDA
}
```

### 3. **Mensajes de Debug Agregados**
El ESP32 ahora imprime en el Monitor Serial cada comando que recibe:
- `>>> COMANDO: GIRAR IZQUIERDA`
- `>>> COMANDO: GIRAR DERECHA`
- `>>> COMANDO: AVANZAR`
- Etc.

## 🔍 Pasos de Diagnóstico

### Paso 1: Verificar qué comando llega al ESP32
1. Abre el **Monitor Serial** en Arduino IDE (115200 baud)
2. Presiona el botón **◄ IZQ** en la interfaz
3. Observa qué mensaje aparece en el serial

**Resultado esperado:**
```
>>> COMANDO: GIRAR IZQUIERDA
```

**Si aparece algo diferente:** El problema está en la GUI de Python.

### Paso 2: Verificar dirección de motores
Si el comando correcto llega pero el carrito no gira correctamente:

#### Prueba Individual de Motores:

**Motor A (IN1/IN2):**
```cpp
// Adelante
digitalWrite(IN1, HIGH);
digitalWrite(IN2, LOW);

// Atrás
digitalWrite(IN1, LOW);
digitalWrite(IN2, HIGH);
```

**Motor B (IN3/IN4):**
```cpp
// Adelante
digitalWrite(IN3, HIGH);
digitalWrite(IN4, LOW);

// Atrás
digitalWrite(IN3, LOW);
digitalWrite(IN4, HIGH);
```

### Paso 3: Verificar cableado L298N

```
ESP32          L298N          Motor
──────────────────────────────────────
GPIO 25  →  IN1  →  Motor A (Izquierdo)
GPIO 26  →  IN2  →  Motor A (Izquierdo)
GPIO 27  →  IN3  →  Motor B (Derecho)
GPIO 14  →  IN4  →  Motor B (Derecho)
GPIO 33  →  ENA  →  PWM Motor A
GPIO 32  →  ENB  →  PWM Motor B
```

## 🔄 Posibles Soluciones

### Solución 1: Invertir funciones de giro
Si al presionar DERECHA gira a la IZQUIERDA (y viceversa), intercambia las funciones en el código:

```cpp
else if (comando == "LEFT") {
  girarDerecha();  // ← Invertido
  client.println("OK:LEFT");
}
else if (comando == "RIGHT") {
  girarIzquierda();  // ← Invertido
  client.println("OK:RIGHT");
}
```

### Solución 2: Invertir un motor
Si el carrito hace algo raro (como gira al revés o hace "S"), invierte las conexiones de **UN SOLO MOTOR**:

**Motor A invertido:**
```cpp
void avanzar() {
  digitalWrite(IN1, LOW);   // ← Invertido
  digitalWrite(IN2, HIGH);  // ← Invertido
  
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
  aplicarVelocidad();
}
```

### Solución 3: Verificar que ambos motores tengan la misma velocidad
Asegúrate de que `aplicarVelocidad()` tenga:
```cpp
ledcWrite(ENA, velocidad);
ledcWrite(ENB, velocidad);  // ← Ambos iguales
```

## 📊 Tabla de Diagnóstico

| Síntoma | Causa Probable | Solución |
|---------|----------------|----------|
| No gira, solo avanza | Funciones de giro incorrectas | Ya corregidas en el código |
| Gira al revés | Funciones invertidas | Intercambiar LEFT/RIGHT |
| Gira en "S" | Motor invertido | Invertir conexiones de 1 motor |
| Gira muy lento | PWM muy bajo | Aumentar velocidad |
| Comandos incorrectos | Problema en GUI | Verificar config.py |

## 🎮 Verificación Final

1. **Sube el código actualizado al ESP32**
2. **Abre el Monitor Serial (115200 baud)**
3. **Ejecuta la aplicación Python**
4. **Prueba cada botón y observa:**
   - ¿Qué comando aparece en el serial?
   - ¿Qué hace el carrito físicamente?

## 📝 Reporta los resultados

**Al presionar ◄ IZQ:**
- Monitor Serial muestra: `_______________`
- Carrito hace: `_______________`

**Al presionar ► DER:**
- Monitor Serial muestra: `_______________`
- Carrito hace: `_______________`

Con esta información podré ayudarte mejor. 🚗
