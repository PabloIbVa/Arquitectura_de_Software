import tkinter as tk
import requests

# Dirección IP de la ESP32
esp32_ip = "172.26.27.81"  # Asegúrate de que esté en la misma red

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

# Botones para modificar el verde
button_on = tk.Button(TitleFrame, text="Encender", bg="green", fg="white", font=("Arial", 10), command=Encender_Led_V)
button_on.place(x=45, y=160)

button_off = tk.Button(TitleFrame, text="Apagar", bg="red", fg="white", font=("Arial", 10), command=Apagar_Led_V)
button_off.place(x=200, y=160)

#Botones para modificar el amarillo

button_on = tk.Button(TitleFrame, text="Encender", bg="green", fg="white", font=("Arial", 10), command=Encender_Led_A)
button_on.place(x=45, y=250)

button_off = tk.Button(TitleFrame, text="Apagar", bg="red", fg="white", font=("Arial", 10), command=Apagar_Led_A)
button_off.place(x=200, y=250)

#Botones para modificar el rojo

button_on = tk.Button(TitleFrame, text="Encender", bg="green", fg="white", font=("Arial", 10), command=Encender_Led_R)
button_on.place(x=45, y=340)

button_off = tk.Button(TitleFrame, text="Apagar", bg="red", fg="white", font=("Arial", 10), command=Apagar_Led_R)
button_off.place(x=200, y=340)

#Fondo de la interfaz

button_close = tk.Button(TitleFrame, text="Cerrar", bg="gray", fg="black", font=("Arial", 10), command=Close_Window)
button_close.place(x=55, y=600)


# Iniciar la interfaz gráfica
cuadro.mainloop()