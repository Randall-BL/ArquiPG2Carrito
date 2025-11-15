#include <WiFi.h>
#include <Wire.h>
#include <WiFiClient.h>
#include "MPU6050.h"

// -------------------------
// WIFI
// -------------------------
const char* ssid = "XXXXX";
const char* password = "XXXXXXX";
WiFiServer server(9000);

// -------------------------
// MOTORES (L298N)
// -------------------------
#define IN1 25
#define IN2 26
#define IN3 27
#define IN4 14

#define ENA 32   // PWM Motor A
#define ENB 33   // PWM Motor B

int velocidad = 200;   // valor inicial PWM (0–255)

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
int16_t ax_anterior = 0;
int16_t ay_anterior = 0;

// Constante de conversión del acelerómetro
const float ACCEL_SCALE = 16384.0;  // Para ±2g
const float GRAVITY = 980.0;  // cm/s²

// =========================
// FUNCIONES DE MOTORES
// =========================
void aplicarVelocidad() {
  ledcWrite(ENA, velocidad);  // ENA - Motor de tracción (usa velocidad variable)
  ledcWrite(ENB, 255);        // ENB - Motor de dirección (siempre a máxima potencia)
}

void detener() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void avanzar() {
  // IN1/IN2: Tracción ADELANTE
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);

  // IN3/IN4: Dirección NEUTRAL (recto)
  //digitalWrite(IN3, LOW);
  //digitalWrite(IN4, LOW);

  aplicarVelocidad();
}

void retroceder() {
  // IN1/IN2: Tracción ATRÁS
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);

  // IN3/IN4: Dirección NEUTRAL (recto)
  //digitalWrite(IN3, LOW);
  //digitalWrite(IN4, LOW);

  aplicarVelocidad();
}

void girarDerecha() {
  // IN1/IN2: Sin tracción (o tracción adelante para girar en movimiento)
  //digitalWrite(IN1, LOW);
  //digitalWrite(IN2, LOW);

  // IN3/IN4: Dirección DERECHA
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  aplicarVelocidad();
}

void girarIzquierda() {
  // IN1/IN2: Sin tracción (o tracción adelante para girar en movimiento)
  //digitalWrite(IN1, LOW);
  //digitalWrite(IN2, LOW);

  // IN3/IN4: Dirección IZQUIERDA
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);

  aplicarVelocidad();
}

// =========================
//   INTERRUPCIÓN HC-SR04
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
  delayMicroseconds(5);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  unsigned long timeout = millis();
  while (!pulseDone && millis() - timeout < 50) {}

  if (!pulseDone) return -1;

  long dt = t_end - t_start;
  return dt * 0.0343 / 2.0;
}

// =========================
// CÁLCULO DE VELOCIDAD MPU6050
// =========================
void calcularVelocidad() {
  int16_t ax, ay, az;
  mpu.getAcceleration(&ax, &ay, &az);
  
  unsigned long tiempoActual = millis();
  float deltaT = (tiempoActual - tiempoAnterior) / 1000.0;  // Convertir a segundos
  
  if (deltaT > 0 && deltaT < 1.0) {  // Evitar divisiones extrañas
    // Convertir aceleración a cm/s²
    float accelX = (ax / ACCEL_SCALE) * GRAVITY;
    float accelY = (ay / ACCEL_SCALE) * GRAVITY;
    
    // Calcular magnitud de aceleración horizontal (plano XY)
    float accelMagnitud = sqrt(accelX * accelX + accelY * accelY);
    
    // Aplicar umbral para eliminar ruido cuando está detenido
    if (abs(accelMagnitud) < 50.0) {  // Umbral de ruido
      accelMagnitud = 0;
    }
    
    // Integrar aceleración para obtener velocidad: v = v0 + a*t
    velocidadActual = velocidadAnterior + (accelMagnitud * deltaT);
    
    // Aplicar factor de decaimiento (simulación de fricción)
    velocidadActual *= 0.95;
    
    // Si el carrito está detenido (PWM = 0 o muy bajo), resetear velocidad
    if (velocidad < 50) {
      velocidadActual *= 0.7;  // Decaimiento rápido
    }
    
    // Limitar velocidad a valores razonables (0-200 cm/s ≈ 0-7 km/h)
    if (velocidadActual < 0) velocidadActual = 0;
    if (velocidadActual > 200) velocidadActual = 200;
    
    velocidadAnterior = velocidadActual;
  }
  
  tiempoAnterior = tiempoActual;
}

float obtenerVelocidadReal() {
  return velocidadActual;  // En cm/s
}


// =========================
// SETUP
// =========================
void setup() {
  Serial.begin(115200);

  // Pines motores
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  // PWM - Nueva API de ESP32 Arduino Core 3.x
  ledcAttach(ENA, 5000, 8);  // pin, frecuencia, resolución
  ledcAttach(ENB, 5000, 8);  // pin, frecuencia, resolución

  aplicarVelocidad();
  detener();

  // HC-SR04
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(ECHO_PIN), echo_ISR, CHANGE);

  // MPU6050
  Wire.begin(22, 21);
  mpu.initialize();
  
  // Inicializar tiempo para cálculo de velocidad
  tiempoAnterior = millis();

  // WIFI
  WiFi.begin(ssid, password);
  Serial.print("Conectando");
  while (WiFi.status() != WL_CONNECTED) { delay(300); Serial.print("."); }
  Serial.println("\nWiFi conectado");
  Serial.println(WiFi.localIP());
  server.begin();
}

// =========================
// LOOP PRINCIPAL
// =========================
void loop() {

  // 1. Calcular velocidad real con MPU6050
  calcularVelocidad();

  // 2. Evitar colisiones
  float d = medirDistancia();
  if (d > 0 && d < 20) {
    Serial.println("⚠️ Obstáculo: " + String(d) + " cm");
    detener();
  }

  // 3. Control por WiFi
  WiFiClient client = server.available();
  if (!client) return;

  unsigned long lastSpeedUpdate = millis();

  while (client.connected()) {
    
    // Actualizar velocidad continuamente
    calcularVelocidad();
    
    // Enviar velocidad periódicamente cada 500ms
    if (millis() - lastSpeedUpdate >= 500) {
      float velReal = obtenerVelocidadReal();
      client.println("SPEED:" + String(velReal, 2));
      lastSpeedUpdate = millis();
    }
    
    if (client.available()) {

      // Leer comando completo (hasta nueva línea)
      String comando = client.readStringUntil('\n');
      comando.trim();

      // -----------------------
      // Comandos de velocidad específica
      // -----------------------
      if (comando.startsWith("SPEED_SET:")) {
        int newSpeed = comando.substring(10).toInt();
        if (newSpeed >= 0 && newSpeed <= 255) {
          velocidad = newSpeed;
          aplicarVelocidad();
          Serial.println("Velocidad PWM = " + String(velocidad));
          // Enviar velocidad real medida por MPU6050
          float velReal = obtenerVelocidadReal();
          client.println("SPEED:" + String(velReal, 2));
        }
      }
      // Velocidad baja
      else if (comando == "SPEED_LOW") {
        velocidad = 150;
        aplicarVelocidad();
        Serial.println("Velocidad BAJA PWM = " + String(velocidad));
        float velReal = obtenerVelocidadReal();
        client.println("SPEED:" + String(velReal, 2));
      }
      // Velocidad alta
      else if (comando == "SPEED_HIGH") {
        velocidad = 255;
        aplicarVelocidad();
        Serial.println("Velocidad ALTA PWM = " + String(velocidad));
        float velReal = obtenerVelocidadReal();
        client.println("SPEED:" + String(velReal, 2));
      }
      // -----------------------
      // Movimientos
      // -----------------------
      else if (comando == "FORWARD") {
        Serial.println(">>> COMANDO: AVANZAR");
        avanzar();
        client.println("OK:FORWARD");
      }
      else if (comando == "BACKWARD") {
        Serial.println(">>> COMANDO: RETROCEDER");
        retroceder();
        client.println("OK:BACKWARD");
      }
      else if (comando == "LEFT") {
        Serial.println(">>> COMANDO: GIRAR IZQUIERDA");
        girarIzquierda();
        client.println("OK:LEFT");
      }
      else if (comando == "RIGHT") {
        Serial.println(">>> COMANDO: GIRAR DERECHA");
        girarDerecha();
        client.println("OK:RIGHT");
      }
      else if (comando == "STOP") {
        Serial.println(">>> COMANDO: DETENER");
        detener();
        client.println("OK:STOP");
      }
      // Comando para consultar velocidad
      else if (comando == "GET_SPEED") {
        float velReal = obtenerVelocidadReal();
        client.println("SPEED:" + String(velReal, 2));  // Velocidad en cm/s con 2 decimales
      }
    }
  }

  client.stop();
}
