#include <WiFi.h>
#include <WebServer.h>

// Configuración de red Wi-Fi
const char *ssid = "Ponki";
const char *password = "ponkilux"; 

// Pines de las unidades (display derecho)
#define a 15
#define b 5
#define c 18
#define d 19
#define e 21 
#define f 22 
#define g 23  

// Pines de las decenas (display izquierdo)
#define a2 13
#define b2 12
#define c2 32
#define d2 27
#define e2 26
#define f2 25 
#define g2 33

// Listas de pines
int unidadesPins[7] = {a, b, c, d, e, f, g};
int decenasPins[7]  = {a2, b2, c2, d2, e2, f2, g2};

// Apagar todos los segmentos
void apagar(int pines[]){
  for(int i = 0; i < 7; i++){
    digitalWrite(pines[i], LOW);
  }
}

// Funciones adicionales para apagar displays
void apagarUnidad() {
  apagar(unidadesPins);
}

void apagarDecena() {
  apagar(decenasPins);
}

// Encender número en display
void numero(int num, int pines[]){
  apagar(pines);
  switch(num){
    case 0:
      digitalWrite(pines[0],HIGH);
      digitalWrite(pines[1],HIGH); 
      digitalWrite(pines[2],HIGH);
      digitalWrite(pines[3],HIGH); 
      digitalWrite(pines[4],HIGH); 
      digitalWrite(pines[5],HIGH); 
      break;
    case 1:
      digitalWrite(pines[1],HIGH);     
      digitalWrite(pines[2],HIGH);
      break;
    case 2: 
      digitalWrite(pines[0],HIGH); 
      digitalWrite(pines[1],HIGH);
      digitalWrite(pines[6],HIGH);
      digitalWrite(pines[4],HIGH);
      digitalWrite(pines[3],HIGH);
      break;
    case 3:
      digitalWrite(pines[0],HIGH);
      digitalWrite(pines[1],HIGH);
      digitalWrite(pines[6],HIGH);
      digitalWrite(pines[2],HIGH);
      digitalWrite(pines[3],HIGH);
      break;
    case 4:
      digitalWrite(pines[5],HIGH);
      digitalWrite(pines[6],HIGH);
      digitalWrite(pines[1],HIGH); 
      digitalWrite(pines[2],HIGH);
      break;
    case 5:
      digitalWrite(pines[0],HIGH);
      digitalWrite(pines[5],HIGH);
      digitalWrite(pines[6],HIGH);
      digitalWrite(pines[2],HIGH);
      digitalWrite(pines[3],HIGH);
      break;
    case 6:
      digitalWrite(pines[0],HIGH);
      digitalWrite(pines[5],HIGH);
      digitalWrite(pines[6],HIGH);
      digitalWrite(pines[2],HIGH);
      digitalWrite(pines[3],HIGH);
      digitalWrite(pines[4],HIGH);
      break;
    case 7: digitalWrite(pines[0],HIGH);
      digitalWrite(pines[1],HIGH);
      digitalWrite(pines[2],HIGH);
      break;
    case 8:
      for (int i=0;i<7;i++)
        digitalWrite(pines[i],HIGH);
      break;
    case 9:
      digitalWrite(pines[0],HIGH);
      digitalWrite(pines[1],HIGH);
      digitalWrite(pines[2],HIGH);
      digitalWrite(pines[3],HIGH);
      digitalWrite(pines[5],HIGH);
      digitalWrite(pines[6],HIGH);
      break;
    default:
      apagar(pines);
  }
}

// Lista de nombres para los números
String nombres[] = {"cero","uno","dos","tres","cuatro","cinco","seis","siete","ocho","nueve"};

// Pines generales (para inicialización)
int pines[] = {15,5,18,19,21,22,23,13,12,32,27,26,25,33};

// Servidor web
WebServer server(80);

void setup() {
  Serial.begin(115200);

  // Configuración de pines
  for (int i = 0 ; i < 14; i++){
    pinMode(pines[i],OUTPUT);
  }
  apagar(unidadesPins);
  apagar(decenasPins);

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

  // Crear rutas dinámicas para las unidades (0 a 9)
  for(int i=0; i<=9; i++){
    String path = "/numero/unidad/" + nombres[i] + "/on";
    server.on(path.c_str(), HTTP_GET, [i](){
      numero(i,unidadesPins);
      server.send(200, "text/plain", "Unidad (" + String(i) + ") encendido");
    });
  }

  // Crear rutas dinámicas para las decenas (0 a 9)
  for(int i=0; i<=9; i++){
    String path = "/numero/decena/" + nombres[i] + "/on";
    server.on(path.c_str(), HTTP_GET, [i](){
      numero(i,decenasPins);
      server.send(200, "text/plain", "Decena (" + String(i) + ") encendido");
    });
  }

  // Ruta para apagar unidad
  server.on("/numero/unidad/off", HTTP_GET, [](){
    apagarUnidad();
    server.send(200, "text/plain", "Unidad apagada");
  });

  // Ruta para apagar decena
  server.on("/numero/decena/off", HTTP_GET, [](){
    apagarDecena();
    server.send(200, "text/plain", "Decena apagada");
  });

  server.begin();
}

void loop() {
  server.handleClient();
}

