#include <WiFi.h>
#include <WebServer.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

// Configuración de red Wi-Fi
const char *ssid = "Ponki";
const char *password = "ponkilux"; 

#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define RELAY_PIN 18
#define ENA 21
#define IN1 22
#define IN2 23

WebServer server(80);

void setup() {
  Serial.begin(115200);

  pinMode(RELAY_PIN, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);

  // Estados iniciales
  digitalWrite(RELAY_PIN, HIGH);  // Relevador apagado
  digitalWrite(ENA, LOW);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);

  dht.begin();

  // Conexión WiFi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\n¡Conectado!");
  Serial.print("IP asignada: ");
  Serial.println(WiFi.localIP());

  // Endpoints HTTP
  server.on("/rele/on", []() {
    digitalWrite(RELAY_PIN, LOW);
    server.send(200, "text/plain", "Focos encendidos");
  });

  server.on("/rele/off", []() {
    digitalWrite(RELAY_PIN, HIGH);
    server.send(200, "text/plain", "Focos apagados");
  });

  server.on("/fan/on", []() {
    digitalWrite(ENA, HIGH);
    digitalWrite(IN1, HIGH);
    server.send(200, "text/plain", "Ventiladores encendidos");
  });

  server.on("/fan/off", []() {
    digitalWrite(ENA, LOW);
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    server.send(200, "text/plain", "Ventiladores apagados");
  });

  server.on("/temperatura/value", []() {
    float temperatura = dht.readTemperature();
    if (isnan(temperatura)) {
      server.send(200, "text/plain", "Error al leer el DHT11");
    } else {
      server.send(200, "text/plain", String(temperatura));
      
    }
  });

  server.begin();
  Serial.println("Servidor web iniciado");
}

void loop() {
  server.handleClient();
}
