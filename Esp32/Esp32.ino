#include <WiFi.h>
#include <Wire.h>
#include <WiFiClient.h>
#include <WiFiAP.h>
#include "MPU6050.h"
#include "driver/gpio.h"
#include "soc/gpio_reg.h"
#include "soc/gpio_struct.h"

// -------------------------
// WIFI
// -------------------------
const char* ssid = "ESP32_Carrito";        // Nombre de la red WiFi
const char* password = "12345678";         // Contraseña (mínimo 8 caracteres)
WiFiServer server(80);

// -------------------------
// SISTEMA DE LOGS
// -------------------------
#define MAX_LOGS 10
String logBuffer[MAX_LOGS];
int logIndex = 0;
int logCount = 0;

// -------------------------
// MOTORES (L298N) - Optimizado con registros
// -------------------------
#define IN1 25
#define IN2 26
#define IN3 27
#define IN4 14

#define ENA 32   // PWM Motor A (Tracción)
#define ENB 33   // PWM Motor B (Dirección)

// Máscaras de bits para acceso directo a registros
#define IN1_MASK (1ULL << IN1)
#define IN2_MASK (1ULL << IN2)
#define IN3_MASK (1ULL << IN3)
#define IN4_MASK (1ULL << IN4)

int velocidad = 200;   // valor inicial PWM (0-255)

// Estado de movimiento
bool moviendoAdelante = false;
bool moviendoAtras = false;
bool girandoDerecha = false;
bool girandoIzquierda = false;

// -------------------------
// HC-SR04
// -------------------------
#define TRIG_PIN 4
#define ECHO_PIN 5

volatile long t_start = 0;
volatile long t_end = 0;
volatile bool pulseDone = false;

// -------------------------
// MPU6050
// -------------------------
MPU6050 mpu;

// Variables para cálculo de velocidad
float velocidadActual = 0.0;  // cm/s
float velocidadAnterior = 0.0;
unsigned long tiempoAnterior = 0;

// Constante de conversión del acelerómetro
const float ACCEL_SCALE = 16384.0;  // Para 2g
const float GRAVITY = 980.0;  // cm/s

// -------------------------
// SISTEMA DE DETECCIÓN DE OBSTÁCULOS
// -------------------------
const float DISTANCIA_INICIO_FRENADO = 90.0;  // cm - Inicia desaceleración
const float DISTANCIA_DETENCION = 45.0;        // cm - Debe estar detenido
const float DISTANCIA_REVERSA = 40.0;          // cm - Activa reversa
const int VELOCIDAD_REVERSA = 255;             // PWM para reversa

bool modoFrenadoAutomatico = false;  // Indica si está frenando automáticamente
bool modoReversaAutomatica = false;  // Indica si está en reversa automática
int velocidadDeseada = 200;          // Velocidad que el usuario quiere
int velocidadOriginal = 200;                  // Velocidad antes del frenado

// -------------------------
// TIMING
// -------------------------
unsigned long lastSensorCheck = 0;
unsigned long lastSpeedUpdate = 0;

// =========================
// FUNCIONES DE LOGS
// =========================
void addLog(const String& message) {
  // Agregar timestamp
  String logMsg = "[" + String(millis()/1000) + "s] " + message;
  
  // Agregar al buffer circular
  logBuffer[logIndex] = logMsg;
  logIndex = (logIndex + 1) % MAX_LOGS;
  if (logCount < MAX_LOGS) logCount++;
  
  // También imprimir en Serial
  Serial.println(logMsg);
}

String getLogsAsJSON() {
  String json = "{\"logs\":[";
  
  int start = (logCount < MAX_LOGS) ? 0 : logIndex;
  for (int i = 0; i < logCount; i++) {
    int idx = (start + i) % MAX_LOGS;
    if (i > 0) json += ",";
    json += "\"" + logBuffer[idx] + "\"";
  }
  
  json += "]}";
  return json;
}

// =========================
// FUNCIONES DE MOTORES
// =========================
void aplicarVelocidad() {
  ledcWrite(ENA, velocidad);  // ENA - Motor de tracción
  ledcWrite(ENB, 255);        // ENB - Motor de dirección (siempre máxima)
}

void detener() {
  // Usando registros directos
  GPIO.out_w1tc = IN1_MASK | IN2_MASK | IN3_MASK | IN4_MASK;  // Clear bits (LOW)
  moviendoAdelante = false;
  moviendoAtras = false;
  girandoDerecha = false;
  girandoIzquierda = false;
  
  // Resetear velocidad calculada del acelerómetro
  velocidadActual = 0;
  velocidadAnterior = 0;
}

void retrocederAutomatico() {
  // Usando registros directos
  GPIO.out_w1tc = IN1_MASK | IN3_MASK | IN4_MASK;  // Clear IN1, IN3, IN4
  GPIO.out_w1ts = IN2_MASK;                        // Set IN2
  ledcWrite(ENA, VELOCIDAD_REVERSA);
  ledcWrite(ENB, 255);
}

void avanzar() {
  if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
    // Usando registros directos
    GPIO.out_w1tc = IN2_MASK;  // Clear IN2
    GPIO.out_w1ts = IN1_MASK;  // Set IN1
    moviendoAdelante = true;
    moviendoAtras = false;
    aplicarVelocidad();
  }
}

void retroceder() {
  // Retroceder SIEMPRE obedece el comando del usuario
  // Cancela cualquier modo automático activo INMEDIATAMENTE
  modoFrenadoAutomatico = false;
  modoReversaAutomatica = false;
  
  // Restaurar velocidad deseada para que el sistema no la resetee
  velocidad = velocidadDeseada;
  
  // Usando registros directos
  GPIO.out_w1tc = IN1_MASK;  // Clear IN1
  GPIO.out_w1ts = IN2_MASK;  // Set IN2
  moviendoAdelante = false;
  moviendoAtras = true;
  aplicarVelocidad();
}

void girarDerecha() {
  if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
    // Usando registros directos
    GPIO.out_w1tc = IN4_MASK;  // Clear IN4
    GPIO.out_w1ts = IN3_MASK;  // Set IN3
    girandoDerecha = true;
    girandoIzquierda = false;
    aplicarVelocidad();
  }
}

void girarIzquierda() {
  if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
    // Usando registros directos
    GPIO.out_w1tc = IN3_MASK;  // Clear IN3
    GPIO.out_w1ts = IN4_MASK;  // Set IN4
    girandoDerecha = false;
    girandoIzquierda = true;
    aplicarVelocidad();
  }
}

// =========================
// INTERRUPCIÓN HC-SR04
// =========================
void IRAM_ATTR echo_ISR() {
  if (digitalRead(ECHO_PIN) == HIGH) {
    t_start = micros();
  } else {
    t_end = micros();
    pulseDone = true;
  }
}

float medirDistancia() {
  pulseDone = false;
  
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  // Timeout de 30ms (suficiente para 5m de alcance, menos consumo)
  unsigned long timeout = millis();
  while (!pulseDone && millis() - timeout < 30) {}

  if (!pulseDone) return -1;

  long dt = t_end - t_start;
  return dt * 0.0343 / 2.0;
}

// =========================
// CÁLCULO DE VELOCIDAD MPU6050
// =========================
void calcularVelocidad() {
  // Solo calcular si ha pasado suficiente tiempo (reduce lecturas I2C)
  unsigned long tiempoActual = millis();
  float deltaT = (tiempoActual - tiempoAnterior) / 1000.0;
  
  if (deltaT < 0.05) return;  // Mínimo 50ms entre lecturas (ahorro I2C)
  
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);
  
  if (deltaT > 0 && deltaT < 1.0) {
    float accelX = (ax / ACCEL_SCALE) * GRAVITY;
    float accelY = (ay / ACCEL_SCALE) * GRAVITY;
    float accelMagnitud = sqrt(accelX * accelX + accelY * accelY);
    
    // Filtro de ruido más agresivo - ignorar aceleraciones muy pequeñas
    if (abs(accelMagnitud) < 80.0) {
      accelMagnitud = 0;
    }
    
    // Si el carro está detenido (velocidad PWM = 0), resetear velocidad calculada
    if (velocidad == 0) {
      velocidadActual = 0;
      velocidadAnterior = 0;
    } else {
      velocidadActual = velocidadAnterior + (accelMagnitud * deltaT);
      velocidadActual *= 0.90;  // Decay más agresivo (era 0.95)
      
      if (velocidad < 50) {
        velocidadActual *= 0.5;  // Reducción más agresiva a baja velocidad (era 0.7)
      }
      
      if (velocidadActual < 0) velocidadActual = 0;
      if (velocidadActual > 200) velocidadActual = 200;
      
      velocidadAnterior = velocidadActual;
    }
  }
  
  tiempoAnterior = tiempoActual;
}

// =========================
// VERIFICACIÓN DE SENSORES Y SEGURIDAD
// =========================
void verificarSensoresSeguridad() {
  calcularVelocidad();
  float d = medirDistancia();
  
  if (d > 0) {
    // NO aplicar lógica de seguridad si el usuario está retrocediendo manualmente
    if (moviendoAtras) {
      // Usuario tiene control manual, no interferir
      return;
    }
    
    if (d < DISTANCIA_REVERSA) {
      if (!modoReversaAutomatica) {
        addLog("EMERGENCIA! Reversa automatica a " + String(d, 1) + "cm");
        modoReversaAutomatica = true;
        modoFrenadoAutomatico = false;
      }
      retrocederAutomatico();
    }
    else if (d < DISTANCIA_DETENCION) {
      if (!modoFrenadoAutomatico || velocidad > 0) {
        addLog("DETENCION! Obstaculo a " + String(d, 1) + "cm");
        modoFrenadoAutomatico = true;
        modoReversaAutomatica = false;
        velocidad = 0;
        detener();
      }
    }
    else if (d < DISTANCIA_INICIO_FRENADO) {
      if (!modoFrenadoAutomatico) {
        addLog("Frenado gradual iniciado a " + String(d, 1) + "cm");
        velocidadOriginal = velocidadDeseada;
        modoFrenadoAutomatico = true;
      }
      modoReversaAutomatica = false;
      float factor = (d - DISTANCIA_DETENCION) / (DISTANCIA_INICIO_FRENADO - DISTANCIA_DETENCION);
      factor = constrain(factor, 0.0, 1.0);
      velocidad = (int)(velocidadOriginal * factor);
      velocidad = constrain(velocidad, 0, 255);
      aplicarVelocidad();
    }
    else {
      // Zona segura - SIEMPRE restaurar control si estaba en modo automático
      if (modoFrenadoAutomatico || modoReversaAutomatica) {
        addLog("Zona segura. Control normal restaurado");
        modoFrenadoAutomatico = false;
        modoReversaAutomatica = false;
        velocidad = velocidadDeseada;
        aplicarVelocidad();
      }
    }
  }
  // Si no hay lectura válida pero estaba en modo automático, seguir verificando
  else if (modoFrenadoAutomatico || modoReversaAutomatica) {
    // Después de 2 segundos sin lectura, restaurar control
    static unsigned long lastValidReading = 0;
    if (lastValidReading == 0) lastValidReading = millis();
    
    if (millis() - lastValidReading > 2000) {
      addLog("Sin lectura de sensor - restaurando control");
      modoFrenadoAutomatico = false;
      modoReversaAutomatica = false;
      velocidad = velocidadDeseada;
      lastValidReading = 0;
    }
  }
}

// =========================
// SETUP
// =========================
void setup() {
  Serial.begin(115200);
  Serial.println("\nIniciando Sistema de Control");

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // PWM a 1kHz
  ledcAttach(ENA, 1000, 8);
  ledcAttach(ENB, 1000, 8);
  
  // Reducir frecuencia del CPU para ahorro de energía
  setCpuFrequencyMhz(80); 
  aplicarVelocidad();
  detener();

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(ECHO_PIN), echo_ISR, CHANGE);

  Wire.begin(22, 21);
  mpu.initialize();
  tiempoAnterior = millis();

  Serial.println("\n--- Configurando WiFi ---");
  // Configurar ESP32 como Access Point con ahorro de energía
  WiFi.mode(WIFI_AP);
  
  // Reducir potencia de transmisión WiFi (ahorro de energía)
  // Rango: 0-20 (0=mínimo, 20=máximo). Usar 8 para balance ahorro/alcance
  WiFi.setTxPower(WIFI_POWER_8_5dBm);  // ~34mA en lugar de ~120mA
  
  WiFi.softAP(ssid, password);
  
  IPAddress IP = WiFi.softAPIP();
  
  Serial.print("✓ Access Point creado: ");
  Serial.println(ssid);
  Serial.print("✓ Contraseña: ");
  Serial.println(password);
  Serial.print("✓ Dirección IP: ");
  Serial.println(IP);
  
  // Iniciar servidor
  server.begin();
  Serial.println("✓ Servidor iniciado en puerto 80");



  lastSensorCheck = millis();
  lastSpeedUpdate = millis();

  addLog("Sistema iniciado correctamente");
  Serial.println("Sistema iniciado");
}


void loop() {
  if (millis() - lastSensorCheck >= 100) {
    verificarSensoresSeguridad();
    lastSensorCheck = millis();
  }

  // Manejar cliente WiFi
  WiFiClient client = server.available();
  if (client) {
    addLog("Cliente conectado");
    lastSpeedUpdate = millis();
    
    while (client.connected()) {
      // Verificar sensores cada 100ms durante conexión
      if (millis() - lastSensorCheck >= 100) {
        verificarSensoresSeguridad();
        lastSensorCheck = millis();
      }
      
      // Enviar velocidad cada 1000ms (1 seg) para reducir tráfico WiFi
      if (millis() - lastSpeedUpdate >= 1000) {
        client.println("SPEED:" + String(velocidadActual, 2));
        lastSpeedUpdate = millis();
      }
      
      // Procesar comandos
      if (client.available()) {
        String comando = client.readStringUntil('\n');
        comando.trim();
        
        if (comando.startsWith("SPEED_SET:")) {
          int newSpeed = comando.substring(10).toInt();
          if (newSpeed >= 0 && newSpeed <= 255) {
            velocidadDeseada = newSpeed;
            if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
              velocidad = newSpeed;
              aplicarVelocidad();
              addLog("Velocidad PWM=" + String(velocidad));
            }
            client.println("SPEED:" + String(velocidadActual, 2));
          }
        }
        else if (comando == "SPEED_LOW") {
          velocidadDeseada = 150;
          if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
            velocidad = 150;
            aplicarVelocidad();
          }
          addLog("Velocidad BAJA");
          client.println("SPEED:" + String(velocidadActual, 2));
        }
        else if (comando == "SPEED_HIGH") {
          velocidadDeseada = 255;
          if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
            velocidad = 255;
            aplicarVelocidad();
          }
          addLog("Velocidad ALTA");
          client.println("SPEED:" + String(velocidadActual, 2));
        }
        else if (comando == "FORWARD") {
          if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
            avanzar();
            addLog("CMD: AVANZAR");
          }
          client.println("OK:FORWARD");
        }
        else if (comando == "BACKWARD") {
          // BACKWARD siempre se ejecuta, sin importar modos automáticos
          retroceder();
          addLog("CMD: RETROCEDER (forzado)");
          client.println("OK:BACKWARD");
        }
        else if (comando == "LEFT") {
          if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
            girarIzquierda();
            addLog("CMD: IZQUIERDA");
          }
          client.println("OK:LEFT");
        }
        else if (comando == "RIGHT") {
          if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
            girarDerecha();
            addLog("CMD: DERECHA");
          }
          client.println("OK:RIGHT");
        }
        else if (comando == "STOP") {
          detener();
          addLog("CMD: DETENER");
          client.println("OK:STOP");
        }
        else if (comando == "GET_SPEED") {
          client.println("SPEED:" + String(velocidadActual, 2));
        }
        else if (comando == "GET_LOGS") {
          // Enviar logs en formato JSON
          client.println("LOGS:" + getLogsAsJSON());
        }
      }
      
      // Delay de 10ms para reducir consumo CPU (suficiente para respuesta rápida)
      delay(10);
    }
    
    client.stop();
    addLog("Cliente desconectado");
  }
  
  // Pequeño delay para reducir consumo CPU en loop vacío
  delay(5);
}
