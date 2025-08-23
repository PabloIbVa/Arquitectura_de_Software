import tkinter as tk
import requests

# Dirección IP de la ESP32
esp32_ip = "192.168.100.84"     # Asegúrate de que esté en la misma red

#Variables para ocupar dentro de rutina semaforo
rutina_activa = False #Menciona si esta activa la rutina
rutina_etapa = 0 #Menciona en que etapa de la rutina va

# Modificamos las funciones originales para ahora solo haya una y con ello disminuir las lineas de código
def send_request(color, state):
    """Envía comando a la ESP32; no truena si no hay conexión."""
    try:
        r = requests.get(f"http://{esp32_ip}/led/{color}/{state}", timeout=1.5)
        print(r.text)
    except requests.exceptions.RequestException as e:
        print(f"[ESP32] {color} -> {state}: {e}")

#Funcion para encender las luces
def encender(c, luces):
    if "rojo" in luces:
        send_request("rojo", "on")
        c.itemconfig(luz_roja, fill="red")
    if "amarillo" in luces:
        send_request("amarillo", "on")
        c.itemconfig(luz_amarilla, fill="yellow")
    if "verde" in luces:
        send_request("verde", "on")
        c.itemconfig(luz_verde, fill="green")

#Funcion para apagar las luces
def apagar(c, luces):
    if "rojo" in luces:
        send_request("rojo", "off")
        c.itemconfig(luz_roja, fill="gray20")
    if "amarillo" in luces:
        send_request("amarillo", "off")
        c.itemconfig(luz_amarilla, fill="gray20")
    if "verde" in luces:
        send_request("verde", "off")
        c.itemconfig(luz_verde, fill="gray20")

# Función para dibujar rectángulos con esquinas redondeadas
def rounded_rectangle(c, x1, y1, x2, y2, r=25, **kwargs):
    """Rectángulo con esquinas redondeadas"""
    points = [
        x1+r, y1,  x2-r, y1,  x2, y1,  x2, y1+r,
        x2, y2-r,  x2, y2,  x2-r, y2,  x1+r, y2,
        x1, y2,    x1, y2-r, x1, y1+r, x1, y1
    ]
    return c.create_polygon(points, smooth=True, **kwargs)

# Funcion para rutina del semaforo
def rutina_semaforo():
    global rutina_etapa
    if not rutina_activa:
        return
    pasos = [
        (lambda: encender(scene, ["verde"]), 4000), # Verde por 4 segundos
        (lambda: apagar(scene, ["verde"]), 100), #Bucle de parpadeo verde
        (lambda: encender(scene, ["verde"]), 500),
        (lambda: apagar(scene, ["verde"]), 500),
        (lambda: encender(scene, ["verde"]), 500),
        (lambda: apagar(scene, ["verde"]), 500),
        (lambda: encender(scene, ["verde"]), 500),
        (lambda: apagar(scene, ["verde"]), 500),
        (lambda: encender(scene, ["amarillo"]), 1500), # Amarillo por 1.5 segundos
        (lambda: apagar(scene, ["amarillo"]), 100),
        (lambda: encender(scene, ["rojo"]), 9500), # Rojo 9.5 s
        (lambda: apagar(scene, ["rojo"]), 100),
    ]
    if rutina_etapa >= len(pasos):
        rutina_etapa = 0 # Repetir indefinidamente
    accion, espera = pasos[rutina_etapa]
    accion()
    rutina_etapa += 1
    root.after(espera, rutina_semaforo)

# Funcion para iniciar la rutina del semaforo
def iniciar_rutina():
    global rutina_activa, rutina_etapa
    if not rutina_activa:
        rutina_activa = True
        rutina_etapa = 0
        rutina_semaforo()

# Funcion para parar la rutina del semaforo
def parar_rutina():
    global rutina_activa
    rutina_activa = False
    apagar(scene, ["rojo", "amarillo", "verde"])
    toggle_reset()

# Seccion de la interfaz grafica
root = tk.Tk()
root.geometry("750x750")
root.title("Interfaz Gráfica del Semáforo")

W, H = 750, 750
scene = tk.Canvas(root, width=W, height=H, highlightthickness=0, bg="#87CEEB")
scene.pack(fill="both", expand=True)

# Cielo con degradado
for i in range(650):
    # Azul cielo variando el canal B
    b = max(100, 235 - i // 3)
    color = f"#{135:02x}{206:02x}{b:02x}"  # (135,206,B)
    scene.create_line(0, i, W, i, fill=color)

# Pasto
scene.create_rectangle(0, 650, W, H, fill="#2e7d32", outline="")

# Poste del semaforo
scene.create_rectangle(543, 540, 557, 740, fill="#424242", outline="")
scene.create_oval(538, 735, 562, 755, fill="#424242", outline="")  # base redondeada

# Semáforo , inclusioj de sombra
sx, sy = 450, 150
rounded_rectangle(scene, sx+48, sy+18, sx+168, sy+398, r=22, fill="#202020", outline="")  # sombra
rounded_rectangle(scene, sx+40, sy+10, sx+160, sy+390, r=22, fill="#0d0d0d", outline="#ffffff", width=3)

# Creamos los circulos del semaforo
luz_roja     = scene.create_oval(sx+60, sy+30,  sx+140, sy+110, fill="gray20", outline="")
luz_amarilla = scene.create_oval(sx+60, sy+140, sx+140, sy+220, fill="gray20", outline="")
luz_verde    = scene.create_oval(sx+60, sy+250, sx+140, sy+330, fill="gray20", outline="")

# Creacion de toggle buttons para cada luz del semaforo
toggle_states = {"rojo": False, "amarillo": False, "verde": False}

# Función para alternar el estado del botón y actualizar el semáforo
def toggle_button(color, btn):
    toggle_states[color] = not toggle_states[color]
    if toggle_states[color]:
        btn.config(bg=("red" if color=="rojo" else "yellow" if color=="amarillo" else "green"),activebackground=("red" if color=="rojo" else "yellow" if color=="amarillo" else "green"))
        encender(scene, [color])
    else:
        btn.config(bg="#5a5a5a", activebackground="#5a5a5a")
        apagar(scene, [color])

# Botones para modificar el rojo
btn_rojo = tk.Button(root, text="", width=6, height=2, relief="flat", bd=0, bg="#5a5a5a",activebackground="#5a5a5a", command=lambda: toggle_button("rojo", btn_rojo))
btn_rojo.place(x=110, y=180)

# Botones para modificar el amarillo
btn_amarillo = tk.Button(root, text="", width=6, height=2, relief="flat", bd=0, bg="#5a5a5a",activebackground="#5a5a5a", command=lambda: toggle_button("amarillo", btn_amarillo))
btn_amarillo.place(x=110, y=240)

# Botones para modificar el verde
btn_verde = tk.Button(root, text="", width=6, height=2, relief="flat", bd=0, bg="#5a5a5a",activebackground="#5a5a5a", command=lambda: toggle_button("verde", btn_verde))
btn_verde.place(x=110, y=300)

# Función para resetear los botones toggle
def toggle_reset():
    for b in (btn_rojo, btn_amarillo, btn_verde):
        b.config(bg="#5a5a5a", activebackground="#5a5a5a")
    toggle_states.update({"rojo": False, "amarillo": False, "verde": False})

# Boton para iniciar rutina
btn_iniciar = tk.Button(root, text="▶ Iniciar Rutina", bg="#1E90FF", fg="white",font=("Arial", 12, "bold"), relief="flat", command=iniciar_rutina)
btn_iniciar.place(x=80, y=420)

# Boton para detener rutina
btn_parar = tk.Button(root, text="⏹ Parar Rutina", bg="orange", fg="black",font=("Arial", 12, "bold"), relief="flat", command=parar_rutina)
btn_parar.place(x=250, y=420)

# Boton para limpiar (apagar todo)
btn_limpiar = tk.Button(root, text="⟲ Limpiar", bg="#bdbdbd", fg="black",font=("Arial", 12, "bold"), relief="flat",command=lambda: (apagar(scene, ["rojo","amarillo","verde"]), toggle_reset()))
btn_limpiar.place(x=150, y=480)

# Boton para cerrar la ventana
btn_cerrar = tk.Button(root, text="❌ Cerrar", bg="#e53935", fg="white",font=("Arial", 12, "bold"), relief="flat", command=root.destroy)
btn_cerrar.place(x=280, y=480)

# Iniciar la interfaz grafica
root.mainloop()
