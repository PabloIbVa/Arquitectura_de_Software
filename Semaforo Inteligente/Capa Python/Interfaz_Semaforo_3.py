import tkinter as tk
import requests

# Dirección IP de la ESP32
esp32_ip = "192.168.100.84"  # Asegúrate de que esté en la misma red

#Variables para ocupar dentro de rutina semaforo
rutina_activa = False #Menciona si esta activa la rutina
rutina_etapa = 0 #Menciona en que etapa de la rutina va

# Función para cerrar la ventana
def Close_Window():
    cuadro.destroy()

# Función para encender el LED VERDE
def Encender_Led_V():
    try:
        response = requests.get(f"http://{esp32_ip}/led/verde/on")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# Función para apagar el LED VERDE 
def Apagar_Led_V():
    try:
        response = requests.get(f"http://{esp32_ip}/led/verde/off")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# Funcion para encender el LED AMARILLO
def Encender_Led_A():
    try:
        response = requests.get(f"http://{esp32_ip}/led/amarillo/on")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# Funcion para apagar el LED AMARILLO
def Apagar_Led_A():
    try:
        response = requests.get(f"http://{esp32_ip}/led/amarillo/off")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# Funcion para encender el LED ROJO
def Encender_Led_R():
    try:
        response = requests.get(f"http://{esp32_ip}/led/rojo/on")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# Funcion para apagar el LED ROJO
def Apagar_Led_R():
    try:
        response = requests.get(f"http://{esp32_ip}/led/rojo/off")
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

# Funcion para encender luces dentro del semaforo interfaz
def encender(canvas,luces):
    # Encender las seleccionadas
    if "rojo" in luces:
        Encender_Led_R()
        canvas.itemconfig(luz_roja, fill="red")
    if "amarillo" in luces:
        Encender_Led_A()
        canvas.itemconfig(luz_amarilla, fill="yellow")
    if "verde" in luces:
        Encender_Led_V()
        canvas.itemconfig(luz_verde, fill="green")

# Funcion para apagar luces dentro del semaforo interfaz
def apagar(canvas,luces):
    # Apagar dependiendo de las seleccionadas
    if "rojo" in luces:
        Apagar_Led_R()
        canvas.itemconfig(luz_roja, fill="white")
    if "amarillo" in luces:
        Apagar_Led_A()
        canvas.itemconfig(luz_amarilla, fill="white")
    if "verde" in luces:
        Apagar_Led_V()
        canvas.itemconfig(luz_verde, fill="white")

#Funcion para rutina del semaforo
def rutina_semaforo():
    global rutina_etapa
    if not rutina_activa:
        return
    pasos = [
        (lambda: encender(canvas, ["verde"]), 4000),   # Verde fijo 4s
        (lambda: apagar(canvas, ["verde"]), 100),      # Apaga verde breve antes de parpadear
        (lambda: encender(canvas, ["verde"]), 500),    # Parpadeo 1
        (lambda: apagar(canvas, ["verde"]), 500),
        (lambda: encender(canvas, ["verde"]), 500),    # Parpadeo 2
        (lambda: apagar(canvas, ["verde"]), 500),
        (lambda: encender(canvas, ["verde"]), 500),    # Parpadeo 3
        (lambda: apagar(canvas, ["verde"]), 500),
        (lambda: encender(canvas, ["amarillo"]), 1500),# Amarillo 1.5s
        (lambda: apagar(canvas, ["amarillo"]), 100),
        (lambda: encender(canvas, ["rojo"]), 9500),    # Rojo 9.5s
        (lambda: apagar(canvas, ["rojo"]), 100),
    ]
    if rutina_etapa >= len(pasos):
        rutina_etapa = 0  # Repetir indefinidamente
    accion, espera = pasos[rutina_etapa]
    accion()
    rutina_etapa += 1
    cuadro.after(espera, rutina_semaforo)

def iniciar_rutina():
    global rutina_activa, rutina_etapa
    if not rutina_activa:
        rutina_activa = True
        rutina_etapa = 0
        rutina_semaforo()

def parar_rutina():
    global rutina_activa
    rutina_activa = False
    apagar(canvas, ["rojo", "amarillo", "verde"])

# Crear la ventana principal de la GUI 
cuadro = tk.Tk()
cuadro.geometry("700x700")
cuadro.title("Interfaz Gráfica del Semáforo")

# Cuadro de fondo
TitleFrame = tk.Frame(cuadro, bg="black", width=700, height=700)
TitleFrame.place(x=0, y=0)

#Semaforo
canvas = tk.Canvas(cuadro, bg="gray", width=200, height=300, highlightthickness=0)
canvas.place(x=400, y=100)
#Creamos los circulos del semaforo 
luz_roja = canvas.create_oval(50, 20, 150, 100, fill="white")
luz_amarilla = canvas.create_oval(50, 110, 150, 190, fill="white")
luz_verde = canvas.create_oval(50, 200, 150, 280, fill="white")

# Botones para modificar el rojo
button_on = tk.Button(TitleFrame, text="Encender", bg="green", fg="white", font=("Arial", 10), command=lambda:encender(canvas,"rojo"))
button_on.place(x=45, y=160)

button_off = tk.Button(TitleFrame, text="Apagar", bg="red", fg="white", font=("Arial", 10), command=lambda:apagar(canvas,"rojo"))
button_off.place(x=200, y=160)

#Botones para modificar el amarillo

button_on = tk.Button(TitleFrame, text="Encender", bg="green", fg="white", font=("Arial", 10), command=lambda:encender(canvas,"amarillo"))
button_on.place(x=45, y=250)

button_off = tk.Button(TitleFrame, text="Apagar", bg="red", fg="white", font=("Arial", 10), command=lambda:apagar(canvas,"amarillo"))
button_off.place(x=200, y=250)

#Botones para modificar el verde

button_on = tk.Button(TitleFrame, text="Encender", bg="green", fg="white", font=("Arial", 10), command=lambda:encender(canvas,"verde"))
button_on.place(x=45, y=340)

button_off = tk.Button(TitleFrame, text="Apagar", bg="red", fg="white", font=("Arial", 10), command=lambda:apagar(canvas,"verde"))
button_off.place(x=200, y=340)

#Boton para iniciar rutina
button_rutina = tk.Button(TitleFrame, text="Iniciar Rutina", bg="blue", fg="white", font=("Arial", 10), command=iniciar_rutina)
button_rutina.place(x=55, y=500)

#Boton para detener rutina
button_parar = tk.Button(TitleFrame, text="Parar Rutina", bg="orange", fg="black", font=("Arial", 10), command=parar_rutina)
button_parar.place(x=150, y=500)

# Botón para cerrar la ventana
button_close = tk.Button(TitleFrame, text="Cerrar", bg="gray", fg="black", font=("Arial", 10), command=Close_Window)
button_close.place(x=55, y=600)

# Boton para limpiar semaforo
button_clear = tk.Button(TitleFrame, text="Limpiar", bg="gray", fg="black", font=("Arial", 10), command=lambda: apagar(canvas, ["rojo", "amarillo", "verde"]))
button_clear.place(x=200, y=600)

# Iniciar la interfaz gráfica
cuadro.mainloop()