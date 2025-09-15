import tkinter as tk
from PIL import Image, ImageTk
import requests

# Dirección IP de la ESP32
esp32_ip = "10.30.108.20"     # Asegúrate de que esté en la misma red

#Variables para ocupar dentro de rutina semaforo
rutina_activa = False #Menciona si esta activa la rutina
rutina_etapa = 0 #Menciona en que etapa de la rutina va

# Modificamos las funciones originales para ahora solo haya una y con ello disminuir las lineas de código
def send_request(color, state):
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
root.geometry("850x750")
root.title("Interfaz Gráfica del Semáforo")

# Frame superior con titulo
frame_top = tk.Frame(root, bg="#87CEEB", height=80)
frame_top.pack(fill="x")
titulo = tk.Label(frame_top, text="User Interface", font=("Arial", 20, "bold"), bg="#87CEEB")
titulo.place(relx=0.5, rely=0.5, anchor="center")

# Comando para insertar imagenes en las esquinas superiores

# Cargar y redimensionar imagen izquierda
logo_izq_img = Image.open("logo_buap.png")
logo_izq_img = logo_izq_img.resize((85, 70), Image.LANCZOS) 
logo_izq = ImageTk.PhotoImage(logo_izq_img)

# Cargar y redimensionar imagen derecha
logo_der_img = Image.open("logo_fcc.png")
logo_der_img = logo_der_img.resize((70, 70), Image.LANCZOS)
logo_der = ImageTk.PhotoImage(logo_der_img)

tk.Label(frame_top, image=logo_izq, bg="#87CEEB").place(x=10, y=10)
tk.Label(frame_top, image=logo_der, bg="#87CEEB").place(x=770, y=10)

W, H = 850, 690
scene = tk.Canvas(root, width=W, height=H, highlightthickness=0, bg="#87CEEB")
scene.pack(fill="both", expand=True)

# Cielo con degradado
for i in range(650):
    b = max(100, 235 - i // 3)
    color = f"#{135:02x}{206:02x}{b:02x}"
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

# Creacion de toggle states para cada luz del semaforo
toggle_states = {"rojo": False, "amarillo": False, "verde": False}

# Diccionario de scales y jobs de parpadeo
parpadeo_scales = {}
parpadeo_jobs = {"rojo": None, "amarillo": None, "verde": None}

# Función para iniciar ciclo de parpadeo
def iniciar_parpadeo(color):
    valor = parpadeo_scales[color][0].get()
    if not toggle_states[color] or valor == 0:
        if parpadeo_jobs[color]:
            root.after_cancel(parpadeo_jobs[color])
            parpadeo_jobs[color] = None
        return

    # Alternar encendido/apagado
    luz = luz_roja if color == "rojo" else luz_amarilla if color == "amarillo" else luz_verde
    current_color = scene.itemcget(luz, "fill")
    if current_color in ("gray20", "black"):
        encender(scene, [color])
    else:
        apagar(scene, [color])

    # Reprogramar parpadeo
    parpadeo_jobs[color] = root.after(valor, iniciar_parpadeo, color)

# Mostrar/ocultar scale al presionar botón
def toggle_button(color, btn):
    toggle_states[color] = not toggle_states[color]
    if toggle_states[color]:
        btn.config(bg=("red" if color=="rojo" else "yellow" if color=="amarillo" else "green"),
                   activebackground=("red" if color=="rojo" else "yellow" if color=="amarillo" else "green"))
        encender(scene, [color])
        parpadeo_scales[color][0].place(x=100, y=(50 if color=="rojo" else 120 if color=="amarillo" else 190))
        parpadeo_scales[color][1].place(x=250, y=(55 if color=="rojo" else 125 if color=="amarillo" else 195))
    else:
        btn.config(bg="#5a5a5a", activebackground="#5a5a5a")
        apagar(scene, [color])
        parpadeo_scales[color][0].place_forget()
        parpadeo_scales[color][1].place_forget()
        if parpadeo_jobs[color]:
            root.after_cancel(parpadeo_jobs[color])
            parpadeo_jobs[color] = None

#Bloque de botones principales
frame_botones = tk.Frame(root, bg="#cccccc", relief="ridge", bd=3)
frame_botones.place(x=50, y=150, width=350, height=270)

#Botones del semaforo
btn_rojo = tk.Button(frame_botones, text="", width=6, height=2, relief="flat", bd=0, bg="#5a5a5a",
                     activebackground="#5a5a5a", command=lambda: toggle_button("rojo", btn_rojo))
btn_rojo.place(x=20, y=30)

btn_amarillo = tk.Button(frame_botones, text="", width=6, height=2, relief="flat", bd=0, bg="#5a5a5a",
                         activebackground="#5a5a5a", command=lambda: toggle_button("amarillo", btn_amarillo))
btn_amarillo.place(x=20, y=100)

btn_verde = tk.Button(frame_botones, text="", width=6, height=2, relief="flat", bd=0, bg="#5a5a5a",
                      activebackground="#5a5a5a", command=lambda: toggle_button("verde", btn_verde))
btn_verde.place(x=20, y=170)

# Reset de botones
def toggle_reset():
    for b in (btn_rojo, btn_amarillo, btn_verde):
        b.config(bg="#5a5a5a", activebackground="#5a5a5a")
    toggle_states.update({"rojo": False, "amarillo": False, "verde": False})
    for sc, sp in parpadeo_scales.values():
        sc.place_forget()
        sp.place_forget()

# Crear scales (ocultos al inicio) -> PWM 0-255 con Spinbox
def crear_scale_spinbox(color, label):
    scale = tk.Scale(frame_botones, from_=0, to=255, resolution=5, orient="horizontal",
                     label=label, bg="#202020", fg="white",
                     highlightthickness=0, troughcolor="#444",
                     command=lambda v: iniciar_parpadeo(color))
    spin = tk.Spinbox(frame_botones, from_=0, to=255, width=5)

    # --- NUEVO: vincular Enter para aplicar valor ---
    def aplicar_valor(event=None):
        try:
            val = int(spin.get())
            scale.set(val)
            iniciar_parpadeo(color)
        except ValueError:
            pass
    spin.bind("<Return>", aplicar_valor)

    # --- Mantener sincronización si se cambia con flechas/spin ---
    spin.config(command=lambda: aplicar_valor())

    return scale, spin

parpadeo_scales["rojo"] = crear_scale_spinbox("rojo", "PWM Rojo (0-255)")
parpadeo_scales["amarillo"] = crear_scale_spinbox("amarillo", "PWM Amarillo (0-255)")
parpadeo_scales["verde"] = crear_scale_spinbox("verde", "PWM Verde (0-255)")

#Bloque de controles extra (más angosto)
frame_controles = tk.Frame(root, bg="#eeeeee", relief="ridge", bd=3)
frame_controles.place(x=100, y=450, width=350, height=120)

# Boton para iniciar rutina
btn_iniciar = tk.Button(frame_controles, text="▶ Iniciar Rutina", bg="#1E90FF", fg="white",
                        font=("Arial", 12, "bold"), relief="flat", command=iniciar_rutina)
btn_iniciar.place(x=20, y=20)

# Boton para detener rutina
btn_parar = tk.Button(frame_controles, text="⏹ Parar Rutina", bg="orange", fg="black",
                      font=("Arial", 12, "bold"), relief="flat", command=parar_rutina)
btn_parar.place(x=180, y=20)

# Boton para limpiar (apagar todo)
btn_limpiar = tk.Button(frame_controles, text="⟲ Limpiar", bg="#bdbdbd", fg="black",
                        font=("Arial", 12, "bold"), relief="flat",
                        command=lambda: (
                            apagar(scene, ["rojo","amarillo","verde"]),
                            toggle_reset(),
                            [sc.set(0) or sp.delete(0, "end") or sp.insert(0, "0")
                             for sc, sp in parpadeo_scales.values()]
                        ))
btn_limpiar.place(x=20, y=70)

# Boton para cerrar la ventana
btn_cerrar = tk.Button(frame_controles, text="❌ Cerrar", bg="#e53935", fg="white",
                       font=("Arial", 12, "bold"), relief="flat", command=root.destroy)
btn_cerrar.place(x=180, y=70)

# Iniciar la interfaz grafica
root.mainloop()
