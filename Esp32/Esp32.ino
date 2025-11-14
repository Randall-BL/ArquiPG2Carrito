/*
 * Control Remoto para Carrito ESP32
 * 
 * Este programa configura el ESP32 como servidor WiFi (Access Point)
 * y controla motores DC mediante un puente H (L298N o similar)
 * basado en comandos recibidos por WiFi desde la aplicación Python.
 * 
 * Autor: Proyecto ArquiPG2Carrito
 * Plataforma: ESP32
 */

#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiAP.h>

// ============= CONFIGURACIÓN WIFI =============
const char* ssid = "ESP32_Carrito";        // Nombre de la red WiFi
const char* password = "12345678";         // Contraseña (mínimo 8 caracteres)

WiFiServer server(80);                     // Servidor en puerto 80

// ============= CONFIGURACIÓN DE PINES =============
// Pines para Motor Izquierdo
const int MOTOR_IZQ_ADELANTE = 26;   // IN1 del L298N
const int MOTOR_IZQ_ATRAS = 27;      // IN2 del L298N
const int MOTOR_IZQ_PWM = 14;        // ENA del L298N (PWM)

// Pines para Motor Derecho
const int MOTOR_DER_ADELANTE = 25;   // IN3 del L298N
const int MOTOR_DER_ATRAS = 33;      // IN4 del L298N
const int MOTOR_DER_PWM = 32;        // ENB del L298N (PWM)

// Pin del LED integrado (opcional, para indicación visual)
const int LED_PIN = 2;

// Pin del sensor de colisión (ejemplo: sensor táctil, ultrasonido, etc.)
// const int SENSOR_COLISION = 34;      // Pin de entrada para sensor de colisión (COMENTADO PARA PRUEBAS)

// ============= CONFIGURACIÓN PWM =============
const int PWM_FREQ = 5000;           // Frecuencia PWM (Hz)
const int PWM_RESOLUTION = 8;        // Resolución 8 bits (0-255)

// Canales PWM
const int PWM_CHANNEL_IZQ = 0;
const int PWM_CHANNEL_DER = 1;

// ============= VARIABLES GLOBALES =============
int velocidadActual = 150;           // Velocidad inicial (0-255)
bool motorActivo = false;
String comandoActual = "STOP";
bool colisionDetectada = false;      // Flag de colisión
unsigned long ultimaColision = 0;    // Timestamp de última colisión

// Variables para prueba manual por Serial
String serialBuffer = "";            // Buffer para comandos del Serial Monitor

// ============= PROTOTIPOS DE FUNCIONES =============
void setupWiFi();
void setupMotors();
void procesarComando(String comando);
void motorAdelante();
void motorAtras();
void motorIzquierda();
void motorDerecha();
void motorDetener();
void setVelocidad(int velocidad);
void parpadearLED(int veces);
void verificarColision();
void enviarAlertaColision(WiFiClient &client);

// ============= SETUP =============
void setup() {
  Serial.begin(115200);
  Serial.println("\n\n=================================");
  Serial.println("Control Remoto Carrito ESP32");
  Serial.println("=================================");
  
  // Configurar LED
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // Configurar sensor de colisión como entrada con pull-up
  // pinMode(SENSOR_COLISION, INPUT_PULLUP);  // COMENTADO PARA PRUEBAS
  
  // Inicializar motores
  setupMotors();
  
  // Inicializar WiFi
  setupWiFi();
  
  Serial.println("\n✓ Sistema listo!");
  Serial.println("Esperando conexiones...");
  Serial.println("\n💡 MODO PRUEBA: Escribe 'R' en el Serial Monitor para simular colisión");
  parpadearLED(3);
}

// ============= LOOP PRINCIPAL =============
void loop() {
  // Leer comandos del Serial Monitor para pruebas (funciona SIN cliente)
  if (Serial.available() > 0) {
    char c = Serial.read();
    
    // Debug: mostrar cada carácter recibido
    Serial.print("DEBUG: Caracter recibido: '");
    Serial.print(c);
    Serial.print("' (ASCII: ");
    Serial.print((int)c);
    Serial.println(")");
    
    // Detectar 'R' o 'r' directamente
    if (c == 'R' || c == 'r') {
      Serial.println("\n🧪 [PRUEBA MANUAL] ¡Comando R detectado!");
      Serial.println("🧪 [PRUEBA MANUAL] Simulando colisión...");
      colisionDetectada = true;
      parpadearLED(3); // Indicador visual
      motorDetener();
    }
  }
  
  WiFiClient client = server.available();
  
  if (client) {
    Serial.println("\n→ Nuevo cliente conectado");
    digitalWrite(LED_PIN, HIGH);
    
    String comandoBuffer = "";
    
    while (client.connected()) {
      // Leer comandos del Serial Monitor mientras está conectado
      if (Serial.available() > 0) {
        char c = Serial.read();
        
        // Debug: mostrar cada carácter recibido
        Serial.print("DEBUG: Caracter recibido: '");
        Serial.print(c);
        Serial.print("' (ASCII: ");
        Serial.print((int)c);
        Serial.println(")");
        
        // Detectar 'R' o 'r' directamente
        if (c == 'R' || c == 'r') {
          Serial.println("\n🧪 [PRUEBA MANUAL] ¡Comando R detectado!");
          Serial.println("🧪 [PRUEBA MANUAL] Simulando colisión...");
          colisionDetectada = true;
          parpadearLED(3); // Indicador visual
          motorDetener();
        }
      }
      
      // Si hay colisión detectada, enviar alerta
      if (colisionDetectada) {
        enviarAlertaColision(client);
        colisionDetectada = false; // Reset flag
      }
      
      if (client.available()) {
        char c = client.read();
        
        if (c == '\n') {
          // Procesar comando completo
          comandoBuffer.trim();
          
          if (comandoBuffer.length() > 0) {
            Serial.print("Comando recibido: ");
            Serial.println(comandoBuffer);
            
            procesarComando(comandoBuffer);
            
            // Enviar confirmación al cliente
            client.println("OK");
            
            comandoBuffer = "";
          }
        } else if (c != '\r') {
          comandoBuffer += c;
        }
      }
      
      delay(1);
    }
    
    // Cliente desconectado
    Serial.println("← Cliente desconectado");
    digitalWrite(LED_PIN, LOW);
    motorDetener();
  }
}

// ============= CONFIGURACIÓN WIFI =============
void setupWiFi() {
  Serial.println("\n--- Configurando WiFi ---");
  
  // Configurar ESP32 como Access Point
  WiFi.mode(WIFI_AP);
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
}

// ============= CONFIGURACIÓN DE MOTORES =============
void setupMotors() {
  Serial.println("\n--- Configurando motores ---");
  
  // Configurar pines como salida
  pinMode(MOTOR_IZQ_ADELANTE, OUTPUT);
  pinMode(MOTOR_IZQ_ATRAS, OUTPUT);
  pinMode(MOTOR_DER_ADELANTE, OUTPUT);
  pinMode(MOTOR_DER_ATRAS, OUTPUT);
  
  // Configurar PWM - Compatible con ESP32 Arduino Core 3.x
  #if ESP_ARDUINO_VERSION >= ESP_ARDUINO_VERSION_VAL(3, 0, 0)
    // Nueva API (ESP32 Core 3.x+)
    ledcAttach(MOTOR_IZQ_PWM, PWM_FREQ, PWM_RESOLUTION);
    ledcAttach(MOTOR_DER_PWM, PWM_FREQ, PWM_RESOLUTION);
  #else
    // API antigua (ESP32 Core 2.x)
    ledcSetup(PWM_CHANNEL_IZQ, PWM_FREQ, PWM_RESOLUTION);
    ledcSetup(PWM_CHANNEL_DER, PWM_FREQ, PWM_RESOLUTION);
    ledcAttachPin(MOTOR_IZQ_PWM, PWM_CHANNEL_IZQ);
    ledcAttachPin(MOTOR_DER_PWM, PWM_CHANNEL_DER);
  #endif
  
  // Iniciar motores detenidos
  motorDetener();
  
  Serial.println("✓ Motores configurados");
  Serial.print("  - Motor Izq: Pines ");
  Serial.print(MOTOR_IZQ_ADELANTE);
  Serial.print(", ");
  Serial.print(MOTOR_IZQ_ATRAS);
  Serial.print(", PWM ");
  Serial.println(MOTOR_IZQ_PWM);
  Serial.print("  - Motor Der: Pines ");
  Serial.print(MOTOR_DER_ADELANTE);
  Serial.print(", ");
  Serial.print(MOTOR_DER_ATRAS);
  Serial.print(", PWM ");
  Serial.println(MOTOR_DER_PWM);
}

// ============= PROCESAMIENTO DE COMANDOS =============
void procesarComando(String comando) {
  comando.toUpperCase();
  
  // Verificar si es un comando de velocidad específica
  if (comando.startsWith("SPEED_SET:")) {
    // Extraer el valor de velocidad
    int separatorIndex = comando.indexOf(':');
    if (separatorIndex > 0) {
      String valorStr = comando.substring(separatorIndex + 1);
      int valor = valorStr.toInt();
      
      if (valor >= 0 && valor <= 255) {
        setVelocidad(valor);
        Serial.print(" Velocidad ajustada: ");
        Serial.println(valor);
        return;
      }
    }
  }
  
  // Comandos normales
  if (comando == "FORWARD") {
    comandoActual = comando;
    motorAdelante();
  }
  else if (comando == "BACKWARD") {
    comandoActual = comando;
    motorAtras();
  }
  else if (comando == "LEFT") {
    comandoActual = comando;
    motorIzquierda();
  }
  else if (comando == "RIGHT") {
    comandoActual = comando;
    motorDerecha();
  }
  else if (comando == "STOP") {
    comandoActual = comando;
    motorDetener();
  }
  else if (comando == "SPEED_LOW") {
    setVelocidad(150);
    Serial.println(" Velocidad BAJA");
  }
  else if (comando == "SPEED_HIGH") {
    setVelocidad(255);
    Serial.println(" Velocidad ALTA");
  }
  else {
    Serial.print("⚠ Comando desconocido: ");
    Serial.println(comando);
  }
}

// ============= CONTROL DE MOTORES =============

void motorAdelante() {
  Serial.println("↑ ADELANTE");
  
  // Motor izquierdo adelante
  digitalWrite(MOTOR_IZQ_ADELANTE, HIGH);
  digitalWrite(MOTOR_IZQ_ATRAS, LOW);
  
  // Motor derecho adelante
  digitalWrite(MOTOR_DER_ADELANTE, HIGH);
  digitalWrite(MOTOR_DER_ATRAS, LOW);
  
  // Aplicar velocidad
  #if ESP_ARDUINO_VERSION >= ESP_ARDUINO_VERSION_VAL(3, 0, 0)
    ledcWrite(MOTOR_IZQ_PWM, velocidadActual);
    ledcWrite(MOTOR_DER_PWM, velocidadActual);
  #else
    ledcWrite(PWM_CHANNEL_IZQ, velocidadActual);
    ledcWrite(PWM_CHANNEL_DER, velocidadActual);
  #endif
  
  motorActivo = true;
}

void motorAtras() {
  Serial.println("↓ ATRÁS");
  
  // Motor izquierdo atrás
  digitalWrite(MOTOR_IZQ_ADELANTE, LOW);
  digitalWrite(MOTOR_IZQ_ATRAS, HIGH);
  
  // Motor derecho atrás
  digitalWrite(MOTOR_DER_ADELANTE, LOW);
  digitalWrite(MOTOR_DER_ATRAS, HIGH);
  
  // Aplicar velocidad
  #if ESP_ARDUINO_VERSION >= ESP_ARDUINO_VERSION_VAL(3, 0, 0)
    ledcWrite(MOTOR_IZQ_PWM, velocidadActual);
    ledcWrite(MOTOR_DER_PWM, velocidadActual);
  #else
    ledcWrite(PWM_CHANNEL_IZQ, velocidadActual);
    ledcWrite(PWM_CHANNEL_DER, velocidadActual);
  #endif
  
  motorActivo = true;
}

void motorIzquierda() {
  Serial.println("← IZQUIERDA");
  
  // Motor izquierdo atrás (o detenido)
  digitalWrite(MOTOR_IZQ_ADELANTE, LOW);
  digitalWrite(MOTOR_IZQ_ATRAS, HIGH);
  
  // Motor derecho adelante
  digitalWrite(MOTOR_DER_ADELANTE, HIGH);
  digitalWrite(MOTOR_DER_ATRAS, LOW);
  
  // Aplicar velocidad (puede ser menor para giro más suave)
  #if ESP_ARDUINO_VERSION >= ESP_ARDUINO_VERSION_VAL(3, 0, 0)
    ledcWrite(MOTOR_IZQ_PWM, velocidadActual * 0.7);  // Motor izq más lento
    ledcWrite(MOTOR_DER_PWM, velocidadActual);         // Motor der normal
  #else
    ledcWrite(PWM_CHANNEL_IZQ, velocidadActual * 0.7);  // Motor izq más lento
    ledcWrite(PWM_CHANNEL_DER, velocidadActual);         // Motor der normal
  #endif
  
  motorActivo = true;
}

void motorDerecha() {
  Serial.println("→ DERECHA");
  
  // Motor izquierdo adelante
  digitalWrite(MOTOR_IZQ_ADELANTE, HIGH);
  digitalWrite(MOTOR_IZQ_ATRAS, LOW);
  
  // Motor derecho atrás (o detenido)
  digitalWrite(MOTOR_DER_ADELANTE, LOW);
  digitalWrite(MOTOR_DER_ATRAS, HIGH);
  
  // Aplicar velocidad
  #if ESP_ARDUINO_VERSION >= ESP_ARDUINO_VERSION_VAL(3, 0, 0)
    ledcWrite(MOTOR_IZQ_PWM, velocidadActual);         // Motor izq normal
    ledcWrite(MOTOR_DER_PWM, velocidadActual * 0.7);  // Motor der más lento
  #else
    ledcWrite(PWM_CHANNEL_IZQ, velocidadActual);         // Motor izq normal
    ledcWrite(PWM_CHANNEL_DER, velocidadActual * 0.7);  // Motor der más lento
  #endif
  
  motorActivo = true;
}

void motorDetener() {
  Serial.println("■ STOP");
  
  // Detener ambos motores
  digitalWrite(MOTOR_IZQ_ADELANTE, LOW);
  digitalWrite(MOTOR_IZQ_ATRAS, LOW);
  digitalWrite(MOTOR_DER_ADELANTE, LOW);
  digitalWrite(MOTOR_DER_ATRAS, LOW);
  
  // PWM a 0
  #if ESP_ARDUINO_VERSION >= ESP_ARDUINO_VERSION_VAL(3, 0, 0)
    ledcWrite(MOTOR_IZQ_PWM, 0);
    ledcWrite(MOTOR_DER_PWM, 0);
  #else
    ledcWrite(PWM_CHANNEL_IZQ, 0);
    ledcWrite(PWM_CHANNEL_DER, 0);
  #endif
  
  motorActivo = false;
}

// ============= CONTROL DE VELOCIDAD =============
void setVelocidad(int velocidad) {
  // Limitar velocidad entre 0 y 255
  velocidadActual = constrain(velocidad, 0, 255);
  
  Serial.print("Velocidad ajustada a: ");
  Serial.println(velocidadActual);
  
  // Si los motores están activos, actualizar velocidad
  if (motorActivo) {
    // Re-procesar el comando actual para aplicar nueva velocidad
    procesarComando(comandoActual);
  }
}

// ============= UTILIDADES =============
void parpadearLED(int veces) {
  for (int i = 0; i < veces; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    delay(100);
  }
}

// ============= DETECCIÓN DE COLISIÓN =============
void verificarColision() {
  // FUNCIÓN DESACTIVADA - Usar comando 'R' en Serial Monitor para pruebas
  // Para activar sensor físico, descomentar el código siguiente:
  
  /*
  // Leer sensor de colisión (LOW = colisión detectada con pull-up)
  int sensorValue = digitalRead(SENSOR_COLISION);
  
  if (sensorValue == LOW) {
    unsigned long tiempoActual = millis();
    if (tiempoActual - ultimaColision > 1000) { // 1 segundo de cooldown
      Serial.println("\n⚠️ ¡COLISIÓN DETECTADA!");
      motorDetener();
      parpadearLED(5);
      colisionDetectada = true;
      ultimaColision = tiempoActual;
    }
  }
  */
}

void enviarAlertaColision(WiFiClient &client) {
  // Enviar mensaje de alerta al cliente
  if (client.connected()) {
    client.println("COLISION_DETECTADA");
    Serial.println("→ Alerta de colisión enviada al cliente");
  }
}

