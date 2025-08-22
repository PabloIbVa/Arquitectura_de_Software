#include <WiFi.h>
#include <WebServer.h>

// Configuración de red Wi-Fi
const char *ssid = "Ponki";
const char *password = "ponkilux"; 

// Asignación de pines
#define PIN_LED_VERDE     21  // Salida LED VERDE
#define PIN_LED_AMARILLO  22  // Salida LED AMARILLO
#define PIN_LED_ROJO      23  // Salida LED ROJO

// Crear un servidor web en el puerto 80
WebServer server(80);

void setup() {
  // Inicialización de la comunicación serie
  Serial.begin(115200);

  // Configuración de pines
  pinMode(PIN_LED_VERDE, OUTPUT);  // Salida LED VERDE
  pinMode(PIN_LED_AMARILLO, OUTPUT);  // Salida LED AMARILLO
  pinMode(PIN_LED_ROJO, OUTPUT);  // Salida LED ROJO
    
  // Conectar a la red Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("¡Conectado!");
  Serial.println(WiFi.localIP()); 

  
  // Rutas para controlar el LED VERDE
  server.on("/led/verde/on", HTTP_GET, []() {
    digitalWrite(PIN_LED_VERDE, HIGH);  // Enciende el LED
    server.send(200, "text/plain", "LED Verde Encendido");
  });

    server.on("/led/verde/off", HTTP_GET, []() {
    digitalWrite(PIN_LED_VERDE, LOW);  // Apaga el LED
    server.send(200, "text/plain", "LED Verde Apagado");
  });


  //Rutas para controlar el LED AMARILLO
  server.on("/led/amarillo/on", HTTP_GET, []() {
    digitalWrite(PIN_LED_AMARILLO, HIGH);  // Enciende el LED
    server.send(200, "text/plain", "LED Amarillo Encendido");
  });

    server.on("/led/amarillo/off", HTTP_GET, []() {
    digitalWrite(PIN_LED_AMARILLO, LOW);  // Apaga el LED
    server.send(200, "text/plain", "LED Amarillo Apagado");
  });

  //Rutas para controlar el LED ROJO
  server.on("/led/rojo/on", HTTP_GET, []() {
    digitalWrite(PIN_LED_ROJO, HIGH);  // Enciende el LED
    server.send(200, "text/plain", "LED Verde Encendido");
  });

    server.on("/led/rojo/off", HTTP_GET, []() {
    digitalWrite(PIN_LED_ROJO, LOW);  // Apaga el LED
    server.send(200, "text/plain", "LED Rojo Apagado");
  });

  // Iniciar el servidor
  server.begin();
  Serial.println("Servidor HTTP iniciado");
}

void loop() {
  // Maneja las solicitudes entrantes
  server.handleClient();
}

