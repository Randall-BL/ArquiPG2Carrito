#include <WiFi.h>
#include <Wire.h>
#include <WiFiClient.h>
#include "MPU6050.h"

// -------------------------
// WIFI
// -------------------------
const char* ssid = "xxxxx";
const char* password = "xxxxx";
WiFiServer server(9000);

// -------------------------
// MOTORES (L298N)
// -------------------------
#define IN1 25
#define IN2 26
#define IN3 27
#define IN4 14

#define ENA 32   // PWM Motor A (Tracción)
#define ENB 33   // PWM Motor B (Dirección)

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
const float DISTANCIA_INICIO_FRENADO = 120.0;  // cm - Inicia desaceleración
const float DISTANCIA_DETENCION = 25.0;        // cm - Debe estar detenido
const float DISTANCIA_REVERSA = 20.0;          // cm - Activa reversa
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
// FUNCIONES DE MOTORES
// =========================
void aplicarVelocidad() {
  ledcWrite(ENA, velocidad);  // ENA - Motor de tracción
  ledcWrite(ENB, 255);        // ENB - Motor de dirección (siempre máxima)
}

void detener() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  moviendoAdelante = false;
  moviendoAtras = false;
  girandoDerecha = false;
  girandoIzquierda = false;
}

void retrocederAutomatico() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  ledcWrite(ENA, VELOCIDAD_REVERSA);
  ledcWrite(ENB, 255);
}

void avanzar() {
  if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    moviendoAdelante = true;
    moviendoAtras = false;
    aplicarVelocidad();
  }
}

void retroceder() {
  // Retroceder SIEMPRE obedece el comando del usuario
  // Cancela cualquier modo automático activo
  modoFrenadoAutomatico = false;
  modoReversaAutomatica = false;
  
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  moviendoAdelante = false;
  moviendoAtras = true;
  aplicarVelocidad();
}

void girarDerecha() {
  if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    girandoDerecha = true;
    girandoIzquierda = false;
    aplicarVelocidad();
  }
}

void girarIzquierda() {
  if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
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
  float deltaT = (tiempoActual - tiempoAnterior) / 1000.0;
  
  if (deltaT > 0 && deltaT < 1.0) {
    float accelX = (ax / ACCEL_SCALE) * GRAVITY;
    float accelY = (ay / ACCEL_SCALE) * GRAVITY;
    float accelMagnitud = sqrt(accelX * accelX + accelY * accelY);
    
    if (abs(accelMagnitud) < 50.0) {
      accelMagnitud = 0;
    }
    
    velocidadActual = velocidadAnterior + (accelMagnitud * deltaT);
    velocidadActual *= 0.95;
    
    if (velocidad < 50) {
      velocidadActual *= 0.7;
    }
    
    if (velocidadActual < 0) velocidadActual = 0;
    if (velocidadActual > 200) velocidadActual = 200;
    
    velocidadAnterior = velocidadActual;
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
    if (d < DISTANCIA_REVERSA) {
      if (!modoReversaAutomatica) {
        Serial.println("EMERGENCIA! Reversa automatica a " + String(d) + " cm");
        modoReversaAutomatica = true;
        modoFrenadoAutomatico = false;
      }
      retrocederAutomatico();
    }
    else if (d < DISTANCIA_DETENCION) {
      if (!modoFrenadoAutomatico || velocidad > 0) {
        Serial.println("DETENCION! Obstaculo a " + String(d) + " cm");
        modoFrenadoAutomatico = true;
        modoReversaAutomatica = false;
        velocidad = 0;
        detener();
      }
    }
    else if (d < DISTANCIA_INICIO_FRENADO) {
      if (!modoFrenadoAutomatico) {
        Serial.println("Iniciando frenado gradual a " + String(d) + " cm");
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
      if (modoFrenadoAutomatico || modoReversaAutomatica) {
        Serial.println("Zona segura. Restaurando control normal.");
        modoFrenadoAutomatico = false;
        modoReversaAutomatica = false;
        velocidad = velocidadDeseada;
        aplicarVelocidad();
      }
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

  ledcAttach(ENA, 5000, 8);
  ledcAttach(ENB, 5000, 8);
  aplicarVelocidad();
  detener();

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(ECHO_PIN), echo_ISR, CHANGE);

  Wire.begin(22, 21);
  mpu.initialize();
  tiempoAnterior = millis();

  WiFi.begin(ssid, password);
  Serial.print("Conectando WiFi");
  while (WiFi.status() != WL_CONNECTED) { 
    delay(300); 
    Serial.print("."); 
  }
  Serial.println("\nWiFi conectado");
  Serial.println("IP: " + WiFi.localIP().toString());
  server.begin();

  lastSensorCheck = millis();
  lastSpeedUpdate = millis();

  Serial.println("Sistema iniciado");
}

// =========================
// LOOP PRINCIPAL
// =========================
void loop() {
  // Verificar sensores cada 50ms
  if (millis() - lastSensorCheck >= 50) {
    verificarSensoresSeguridad();
    lastSensorCheck = millis();
  }

  // Manejar cliente WiFi
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Cliente conectado");
    lastSpeedUpdate = millis();
    
    while (client.connected()) {
      // Verificar sensores durante la conexión
      if (millis() - lastSensorCheck >= 50) {
        verificarSensoresSeguridad();
        lastSensorCheck = millis();
      }
      
      // Enviar velocidad cada 500ms
      if (millis() - lastSpeedUpdate >= 500) {
        client.println("SPEED:" + String(velocidadActual, 2));
        lastSpeedUpdate = millis();
      }
      
      // Procesar comandos
      if (client.available()) {
        String comando = client.readStringUntil('\n');
        comando.trim();
        Serial.println("Recibido: " + comando);
        
        if (comando.startsWith("SPEED_SET:")) {
          int newSpeed = comando.substring(10).toInt();
          if (newSpeed >= 0 && newSpeed <= 255) {
            velocidadDeseada = newSpeed;
            if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
              velocidad = newSpeed;
              aplicarVelocidad();
              Serial.println("Velocidad PWM = " + String(velocidad));
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
          client.println("SPEED:" + String(velocidadActual, 2));
        }
        else if (comando == "SPEED_HIGH") {
          velocidadDeseada = 255;
          if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
            velocidad = 255;
            aplicarVelocidad();
          }
          client.println("SPEED:" + String(velocidadActual, 2));
        }
        else if (comando == "FORWARD") {
          if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
            avanzar();
            Serial.println("CMD: FORWARD");
          }
          client.println("OK:FORWARD");
        }
        else if (comando == "BACKWARD") {
          // BACKWARD siempre se ejecuta, sin importar modos automáticos
          retroceder();
          Serial.println("CMD: BACKWARD (forzado)");
          client.println("OK:BACKWARD");
        }
        else if (comando == "LEFT") {
          if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
            girarIzquierda();
            Serial.println("CMD: LEFT");
          }
          client.println("OK:LEFT");
        }
        else if (comando == "RIGHT") {
          if (!modoFrenadoAutomatico && !modoReversaAutomatica) {
            girarDerecha();
            Serial.println("CMD: RIGHT");
          }
          client.println("OK:RIGHT");
        }
        else if (comando == "STOP") {
          detener();
          Serial.println("CMD: STOP");
          client.println("OK:STOP");
        }
        else if (comando == "GET_SPEED") {
          client.println("SPEED:" + String(velocidadActual, 2));
        }
      }
      
      delay(5);
    }
    
    client.stop();
    Serial.println("Cliente desconectado");
  }
}
