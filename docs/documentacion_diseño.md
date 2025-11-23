# Documentación de Diseño 
**Proyecto:**  Robot basado en microcontrolador  
**Versión:** 1.0  
**MCU:** ESP32

---


## 2. Arquitectura del software embebido

### 2.1 Módulos

En la arquitectura del software, se encuentran los siguientes módulos:

1. **Comunicación WiFi**
   - Configuración de la red mediante los parámetros de `ssid` y `password`.
   - Un servidor TCP (`WiFiServer server(9000)`).
   - Protocolo de comandos de texto con instrucciones como: FORWARD, BACKWARD y SPEED_SET.

2. **Control de motores (L298N)**
   - Pines digitales de dirección: `IN1`, `IN2`, `IN3`, `IN4`.
   - Canales PWM: `ENA` (usado para la traccióntracción), `ENB` (usado para la dirección).
   - Funciones de alto nivel:
     - `aplicarVelocidad()`
     - `detener()`
     - `avanzar()`
     - `retroceder()`
     - `retrocederAutomatico()`
     - `girarDerecha()`
     - `girarIzquierda()`
   - Estados de movimiento: `moviendoAdelante`, `moviendoAtras`, `girandoDerecha`, `girandoIzquierda`.

3. **Sensor de distancia (HC-SR04)**
   - Pines: `TRIG_PIN`, `ECHO_PIN`.
   - Interrupción `echo_ISR()` sobre flancos del pin ECHO.
   - Captura de tiempos `t_start`, `t_end` y bandera de finalización `pulseDone`.
   - Función de medición no bloqueante: `medirDistancia()`.

4. **Acelerómetro y Giroscopio (MPU6050)**
   - Interfaz I²C (`Wire.begin(22, 21)`).
   - Objeto `MPU6050 mpu`.
   - Cálculo de velocidad: `calcularVelocidad()`.

5. **Lógica de seguridad y control automático**
   - Parámetros:
     - Distancias umbral: `DISTANCIA_INICIO_FRENADO`, `DISTANCIA_DETENCION`, `DISTANCIA_REVERSA`.
     - Velocidad de reversa: `VELOCIDAD_REVERSA`.
   - Estados:
     - `modoFrenadoAutomatico`
     - `modoReversaAutomatica`
     - `velocidadDeseada`, `velocidadOriginal`, `velocidad` (PWM efectiva).
   - Función central: `verificarSensoresSeguridad()`.

6. **Timing**
   - Ticks de sistema con `millis()`:
     - `lastSensorCheck` para sensado/seguridad (cada 50 ms).
     - `lastSpeedUpdate` para telemetría de velocidad (cada 500 ms).

### 2.2 Diagramas de flujo del sistema

Diagrama de funcionamiento general

![Diagrama de funcionamiento general](imgs/FlujoGeneral.jpg)

Diagrama de flujo del setup()

![Diagrama de setup](imgs/FlujoSetup.jpg)

Diagrama de flujo del loop()

![Diagrama de setup](imgs/FlujoLoop.jpg)

Diagrama de la verificación de sensores

![Diagrama de setup](imgs/FlujoSensores.jpg)

## 2.3 Estrategias de gestión de E/S

### 2.3.1 Motores (salidas digitales y PWM)

**Dirección de tracción:**

- `IN1`, `IN2` controlan el sentido (adelante/atrás) del motor de tracción.

**Dirección de giro:**

- `IN3`, `IN4` controlan la dirección (izquierda/derecha) del motor de dirección.

**Magnitud de velocidad:**

- `ENA`: PWM para la tracción (`ledcWrite(ENA, velocidad)`).
- `ENB`: PWM fijo a `255` para la dirección (siempre máximo giro disponible).

El software abstrae el control mediante funciones de alto nivel:

- `avanzar()`
- `retroceder()`
- `girarDerecha()`
- `girarIzquierda()`
- `detener()`

Estas funciones consultan y/o actualizan estados de seguridad:

- `modoFrenadoAutomatico`
- `modoReversaAutomatica`


### 2.3.2 Sensor HC-SR04 (entrada digital + interrupciones)

**Lanzamiento del pulso:**

- `TRIG_PIN` se pone brevemente en `HIGH` para iniciar la medición (≈ 10 µs).

**Captura del eco con interrupción:**

- Interrupción `echo_ISR()` en los flancos de `ECHO_PIN`:
  - Flanco de subida: `t_start = micros()`.
  - Flanco de bajada: `t_end = micros(); pulseDone = true;`.

**Lectura no bloqueante:**

La función `medirDistancia()`:

1. Limpia la bandera: `pulseDone = false`.
2. Dispara el pulso en `TRIG`.
3. Espera con timeout controlado por `millis()` (máx. 50 ms).
4. Si `pulseDone == true`, calcula la distancia a partir de `t_end - t_start`.
5. Si hay timeout, retorna `-1` (lectura inválida).

Esta estrategia reduce la carga de CPU al no emplear `pulseIn()` (bloqueante) y permite seguir atendiendo otras tareas en el bucle principal.


### 2.3.3 Sensor MPU6050 (I²C)

- Se inicializa con:
  - `Wire.begin(22, 21)`
  - `mpu.initialize()`

La función `calcularVelocidad()`:

1. Lee las aceleraciones en ejes `X` e `Y`.
2. Calcula la magnitud lateral `accelMagnitud`.
3. Aplica:
   - Umbral de ruido (ignorando aceleraciones pequeñas).
   - Integración numérica:  
     `velocidad = velocidadAnterior + a * Δt`.
   - Filtro de amortiguamiento (multiplicación por `0.95`).
   - Reducción extra si el PWM es bajo (`velocidad < 50`).
   - Saturación de la velocidad al rango `[0, 200]`.

La velocidad resultante se usa para telemetría y, potencialmente, para futuras lógicas de control.


### 2.3.4 Interrupciones, prioridades y sincronización

#### Interrupción del HC-SR04

**ISR principal:**

- `void IRAM_ATTR echo_ISR();`

**Variables compartidas:**

- `volatile long t_start, t_end;`
- `volatile bool pulseDone;`

**Sincronización:**

- El bucle principal (`loop()`) y `verificarSensoresSeguridad()` leen `pulseDone` y los tiempos (`t_start`, `t_end`).
- `pulseDone` actúa como bandera para indicar que una medición está lista.
- El acceso es simple (lectura/escritura atómica sobre tipos primitivos), por lo que el riesgo de condiciones de carrera es mínimo en este contexto.


#### Priorización implícita

**Seguridad > Comandos del usuario**

- `verificarSensoresSeguridad()` se ejecuta periódicamente:
  - En el `loop()` general.
  - Dentro del bucle de atención al cliente TCP.

**Modos automáticos:**

- **Frenado automático** (`modoFrenadoAutomatico`):
  - Limita o lleva a cero la velocidad PWM.
  - Inhibe la ejecución de comandos de avance y giro.

- **Reversa automática** (`modoReversaAutomatica`):
  - Fuerza `retrocederAutomatico()` (con `IN2` activo y velocidad de reversa máxima).

**Excepción controlada:**

- El comando `BACKWARD` del usuario **siempre** se respeta:
  - Resetea `modoFrenadoAutomatico` y `modoReversaAutomatica`.
  - Ejecuta `retroceder()` aun cuando haya obstáculos cerca.

Esto permite al usuario sacar el vehículo de situaciones de bloqueo, asumiendo que conoce el entorno y los riesgos.

### 2.4 Protocolos de comunicación

#### 2.4.1 Pila de protocolos

- **Capa física/enlace:**  
  WiFi (IEEE 802.11, manejado por el stack del ESP32).

- **Capa de transporte:**  
  TCP (conexión orientada, fiable).

- **Capa de aplicación:**  
  Protocolo propio basado en líneas de texto ASCII.


#### 2.4.2 Protocolo de aplicación (definido en el código)

**Formato de mensajes**

- **Comandos desde el cliente:**
  - Línea ASCII terminada en `'\n'`.
  - El servidor usa `readStringUntil('\n')` para leer cada comando.

- **Respuestas / telemetría del ESP32:**
  - Líneas tipo:
    - `SPEED:<valor>` → velocidad estimada en cm/s, con 2 decimales.
    - `OK:<COMANDO>` → confirmaciones simples de comandos recibidos.

**Comandos soportados**

- `SPEED_SET:<0-255>`  
  Cambia `velocidadDeseada` (y `velocidad` si no hay modos automáticos activos).

- `SPEED_LOW`  
  Fija `velocidadDeseada = 150`.

- `SPEED_HIGH`  
  Fija `velocidadDeseada = 255`.

- `FORWARD`  
  Intenta avanzar (si no hay frenado/reversa automáticos activos).

- `BACKWARD`  
  Siempre ejecuta reversa (anula modos automáticos).

- `LEFT`, `RIGHT`  
  Giros si la lógica de seguridad lo permite.

- `STOP`  
  Detiene el vehículo.

- `GET_SPEED`  
  Solicita lectura inmediata de `velocidadActual`.


#### 2.4.3 Telemetría

- Cada **500 ms**, cuando hay un cliente conectado:
  - Se envía `SPEED:<velocidadActual>` de forma periódica.

- Después de algunos comandos (por ejemplo `SPEED_SET`):
  - Se responde también con una línea `SPEED:` actualizada, para facilitar *feedback* inmediato en la interfaz del usuario.


#### 2.4.4 Análisis comparativo de la solución de comunicación

##### TCP + protocolo de texto 

**Ventajas:**

- Fiabilidad (retransmisiones, orden de llegada garantizado por TCP).
- Implementación sencilla:
  - Lado embebido: lectura de líneas y estructura `if/else` por comando.
  - Lado cliente: puede ser cualquier lenguaje capaz de abrir un socket TCP.
- Flexibilidad para depuración:
  - Se puede probar desde un terminal TCP (`telnet`, `netcat`, etc.).

**Desventajas:**

- Overhead mayor que UDP, especialmente si la red tiene pérdida de paquetes.
- No incluye estructura de mensaje binaria por defecto (se está usando texto, con más bytes por parámetro).

### 2.5 Organización de memoria

En el entorno **ESP32 con Arduino**, la memoria de programa y de datos se organiza (a alto nivel) en:

- **Memoria de programa (Flash):**
  - Código compilado de:
    - Lógica de control de motores, seguridad y comunicaciones.
    - Bibliotecas (`WiFi`, `Wire`, `MPU6050`, etc.).

- **Memoria de datos (RAM):**
  - **Segmento de datos estáticos:**
    - Variables globales inicializadas (por ejemplo `ssid`, `password`, umbrales de distancia).
  - **Segmento BSS:**
    - Variables globales no inicializadas o inicializadas a cero (por ejemplo *flags*, tiempos, etc.).
  - **Stack:**
    - Variables locales de funciones (por ejemplo `comando` en el `loop()`, variables temporales en `calcularVelocidad()`).
  - **Heap:**
    - Usado internamente por librerías (por ejemplo `String`, `WiFi`, etc.).

El diseño evita el uso explícito de memoria dinámica por parte del usuario (no hay `new` / `malloc` en el código), lo cual simplifica el análisis de consumo de memoria y reduce el riesgo de fragmentación.

