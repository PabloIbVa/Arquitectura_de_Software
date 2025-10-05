#include <Adafruit_Sensor.h>
#include <DHT.h>

#include <DHT_U.h>

#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const int ENA = 21;   
const int IN1 = 22;
const int IN2 = 23;

const int RELAY_PIN = 18;  

float tempRequerida = 20.0;

void setup() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(RELAY_PIN, OUTPUT);

  Serial.begin(115200);
  dht.begin();

  Serial.println("Sistema de Control de Temperatura (ESP32 + DHT11)");
}

void loop() {
  delay(2000);

  float temperatura = dht.readTemperature();

  if (isnan(temperatura)) {
    Serial.println("Error al leer el DHT11");
    return;
  }

  Serial.print("Temperatura actual: ");
  Serial.print(temperatura);
  Serial.println(" °C");

  if (temperatura < tempRequerida - 1) {
    digitalWrite(RELAY_PIN, LOW);  // Activar relé
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(ENA, LOW);
    Serial.println("Encendiendo FOCOS (Calefacción)");
  } 
  else if (temperatura > tempRequerida + 1) {
    digitalWrite(RELAY_PIN, HIGH); // Apagar focos
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(ENA, HIGH);
    Serial.println("Encendiendo VENTILADORES");
  } 
  else {
    digitalWrite(RELAY_PIN, HIGH);
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(ENA, LOW);
    Serial.println("Temperatura OK → Todo apagado");
  }
}
