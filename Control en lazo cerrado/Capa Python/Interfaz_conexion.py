import tkinter as tk
from tkinter import messagebox
import threading
import requests
import time

# ============================
# CONFIGURACIÓN
# ============================
ESP_INVERNADERO = "http://192.168.100.81"
ESP_DISPLAY = "http://192.168.100.79"

# ============================
# VARIABLES GLOBALES
# ============================
estado_actual = {"foco": False, "ventilador": False}
stop_temp_updater = threading.Event()
stop_control_loop = threading.Event()
temp_lock = threading.Lock()
current_temperature = None
ultimo_numero_mostrado = {"decenas": None, "unidades": None}
display_lock = threading.Lock()
control_thread_lock = threading.Lock()
control_thread = None

# ============================
# FUNCIONES DE RED Y CONTROL
# ============================
def obtener_temperatura():
    try:
        r = requests.get(f"{ESP_INVERNADERO}/temperatura/value", timeout=3)
        if r.status_code == 200:
            return float(r.text.strip())
    except Exception:
        return None
    return None

def numero_a_nombre(n):
    nombres = ["cero","uno","dos","tres","cuatro","cinco","seis","siete","ocho","nueve"]
    if 0 <= n < len(nombres): return nombres[n]
    return "cero"

def mostrar_en_display(temp):
    global ultimo_numero_mostrado
    try:
        entero = int(temp)
        d, u = entero // 10, entero % 10
        with display_lock:
            if ultimo_numero_mostrado["decenas"] != d:
                requests.get(f"{ESP_DISPLAY}/numero/decena/{numero_a_nombre(d)}/on", timeout=2)
                ultimo_numero_mostrado["decenas"] = d
            if ultimo_numero_mostrado["unidades"] != u:
                requests.get(f"{ESP_DISPLAY}/numero/unidad/{numero_a_nombre(u)}/on", timeout=2)
                ultimo_numero_mostrado["unidades"] = u
    except Exception: pass

def apagar_todo():
    try:
        requests.get(f"{ESP_INVERNADERO}/rele/off", timeout=2)
        requests.get(f"{ESP_INVERNADERO}/fan/off", timeout=2)
    except Exception: pass
    estado_actual["foco"] = False
    estado_actual["ventilador"] = False

def encender_foco(on=True):
    try:
        if on:
            requests.get(f"{ESP_INVERNADERO}/rele/on", timeout=2)
            estado_actual["foco"] = True
        else:
            requests.get(f"{ESP_INVERNADERO}/rele/off", timeout=2)
            estado_actual["foco"] = False
    except Exception: pass

def encender_ventilador(on=True):
    try:
        if on:
            requests.get(f"{ESP_INVERNADERO}/fan/on", timeout=2)
            estado_actual["ventilador"] = True
        else:
            requests.get(f"{ESP_INVERNADERO}/fan/off", timeout=2)
            estado_actual["ventilador"] = False
    except Exception: pass

# ============================
# HILOS
# ============================
def temperature_updater(root, var, update_interval=2):
    global current_temperature
    while not stop_temp_updater.is_set():
        t = obtener_temperatura()
        if t is not None:
            with temp_lock: current_temperature = t
            root.after(0, lambda: var.set(f"{t:.2f} °C"))
            threading.Thread(target=mostrar_en_display, args=(t,), daemon=True).start()
        else:
            root.after(0, lambda: var.set("Sin lectura"))
        time.sleep(update_interval)

def control_loop_fn(root, desired_var, status_var, histeresis=0.5, poll=2):
    global current_temperature
    while not stop_control_loop.is_set():
        with temp_lock:
            t = current_temperature
        if t is None: t = obtener_temperatura()
        if t is None:
            root.after(0, lambda: status_var.set("Sin lectura"))
            time.sleep(poll)
            continue
        try: deseada = float(desired_var.get())
        except: continue

        if t > (deseada + histeresis):
            encender_ventilador(True)
            encender_foco(False)
            root.after(0, lambda: status_var.set("🌀 Enfriando (ventilador ON)"))
        elif t < (deseada - histeresis):
            encender_foco(True)
            encender_ventilador(False)
            root.after(0, lambda: status_var.set("💡 Calentando (foco ON)"))
        else:
            apagar_todo()
            root.after(0, lambda: status_var.set("🌿 Temperatura estable (todo OFF)"))
        time.sleep(poll)
    apagar_todo()
    root.after(0, lambda: status_var.set("Control detenido (todo apagado)"))

# ============================
# INTERFAZ PRINCIPAL
# ============================
class InvernaderoApp:
    def __init__(self, root):
        global control_thread
        self.root = root
        self.root.title("🌱 Sistema de Control de Invernadero")
        self.root.geometry("600x450")
        self.root.configure(bg="#e9f5e9")

        self.current_temp_var = tk.StringVar(value="Esperando...")
        self.status_var = tk.StringVar(value="Estado: -")
        self.desired_temp_var = tk.StringVar(value="28.0")
        self.foco_t = tk.IntVar(value=10)
        self.vent_t = tk.IntVar(value=10)

        # Encabezado
        header = tk.Frame(root, bg="#66bb6a")
        header.pack(fill=tk.X)
        tk.Label(header, text="🌿 Control de Invernadero", bg="#66bb6a", fg="white",
                 font=("Arial", 16, "bold")).pack(pady=8)

        # Dibujo simbólico
        dibujo = tk.Label(root, text="🏡\n╔═══════════╗\n║  🌱🌸🌿  ║\n╚═══════════╝",
                          font=("Courier", 18), bg="#e9f5e9", fg="#388e3c")
        dibujo.pack(pady=10)

        # Botones principales
        botones = tk.Frame(root, bg="#e9f5e9")
        botones.pack()
        self.boton_principal = tk.Button(botones, text="🏠 Principal", width=16, bg="#a5d6a7",
                                         command=self.show_main)
        self.boton_manual = tk.Button(botones, text="🧑‍🌾 Lazo Abierto", width=16, bg="#a5d6a7",
                                      command=self.show_manual)
        self.boton_auto = tk.Button(botones, text="🤖 Lazo Cerrado", width=16, bg="#a5d6a7",
                                    command=self.show_auto)
        for b in (self.boton_principal, self.boton_manual, self.boton_auto):
            b.pack(side=tk.LEFT, padx=8, pady=5)

        # Contenedor principal
        self.contenido = tk.Frame(root, bg="#f1f8e9", bd=2, relief=tk.RIDGE)
        self.contenido.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Frames
        self.frame_main = tk.Frame(self.contenido, bg="#f1f8e9")
        self.frame_manual = tk.Frame(self.contenido, bg="#f1f8e9")
        self.frame_auto = tk.Frame(self.contenido, bg="#f1f8e9")

        self.build_main()
        self.build_manual()
        self.build_auto()
        self.show_main()

        # Footer
        footer = tk.Frame(root, bg="#e9f5e9")
        footer.pack(side=tk.BOTTOM, pady=6)
        tk.Label(footer, text="🌡 Temperatura:", bg="#e9f5e9").grid(row=0, column=0)
        tk.Label(footer, textvariable=self.current_temp_var, font=("Courier", 14),
                 bg="#e9f5e9").grid(row=0, column=1, padx=8)
        tk.Label(footer, text="🔧 Estado:", bg="#e9f5e9").grid(row=1, column=0)
        tk.Label(footer, textvariable=self.status_var, bg="#e9f5e9").grid(row=1, column=1, padx=8)

        # Iniciar hilo temperatura
        stop_temp_updater.clear()
        threading.Thread(target=temperature_updater, args=(root, self.current_temp_var), daemon=True).start()

        # Evento de cierre
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------- FRAMES ----------
    def build_main(self):
        f = self.frame_main
        for w in f.winfo_children(): w.destroy()
        tk.Label(f, text="🌞 Bienvenido al Sistema de Invernadero 🌞", bg="#f1f8e9",
                 font=("Arial", 13, "bold"), fg="#2e7d32").pack(pady=10)
        tk.Label(f, text="Monitorea y controla la temperatura dentro del invernadero.\n"
                         "Puedes usar el modo Manual o el modo Automático.", bg="#f1f8e9").pack(pady=10)
        tk.Label(f, text="Selecciona una opción arriba para comenzar.", bg="#f1f8e9",
                 font=("Arial", 10, "italic")).pack(pady=10)

    def build_manual(self):
        f = self.frame_manual
        for w in f.winfo_children(): w.destroy()

        titulo = tk.Label(f, text="🧑‍🌾 Control Manual (Lazo Abierto)", bg="#f1f8e9",
                          font=("Arial", 13, "bold"), fg="#1b5e20")
        titulo.pack(pady=6)

        cont = tk.Frame(f, bg="#f1f8e9")
        cont.pack(pady=5)

        # Sección Foco
        foco_frame = tk.LabelFrame(cont, text="💡 Foco", bg="#f1f8e9", fg="#2e7d32",
                                   font=("Arial", 11, "bold"), padx=10, pady=6)
        foco_frame.grid(row=0, column=0, padx=10, pady=8)
        tk.Label(foco_frame, text="Tiempo (s):", bg="#f1f8e9").pack()
        tk.Entry(foco_frame, textvariable=self.foco_t, width=6).pack(pady=3)
        tk.Button(foco_frame, text="Encender (Temporizado)", width=20,
                  bg="#c8e6c9", command=self._foco_temp).pack(pady=2)
        tk.Button(foco_frame, text="Encender Indefinido", width=20,
                  bg="#aed581", command=lambda: encender_foco(True)).pack(pady=2)
        tk.Button(foco_frame, text="Apagar Foco", width=20,
                  bg="#ef9a9a", command=lambda: encender_foco(False)).pack(pady=2)

        # Sección Ventilador
        vent_frame = tk.LabelFrame(cont, text="🌀 Ventilador", bg="#f1f8e9", fg="#2e7d32",
                                   font=("Arial", 11, "bold"), padx=10, pady=6)
        vent_frame.grid(row=0, column=1, padx=10, pady=8)
        tk.Label(vent_frame, text="Tiempo (s):", bg="#f1f8e9").pack()
        tk.Entry(vent_frame, textvariable=self.vent_t, width=6).pack(pady=3)
        tk.Button(vent_frame, text="Encender (Temporizado)", width=20,
                  bg="#c8e6c9", command=self._vent_temp).pack(pady=2)
        tk.Button(vent_frame, text="Encender Indefinido", width=20,
                  bg="#aed581", command=lambda: encender_ventilador(True)).pack(pady=2)
        tk.Button(vent_frame, text="Apagar Ventilador", width=20,
                  bg="#ef9a9a", command=lambda: encender_ventilador(False)).pack(pady=2)

        tk.Button(f, text="Apagar Todo", width=25, bg="#f44336", fg="white",
                  command=lambda: [apagar_todo(), self.status_var.set("Man: Todo OFF")]).pack(pady=10)

    def build_auto(self):
        f = self.frame_auto
        for w in f.winfo_children(): w.destroy()

        tk.Label(f, text="🤖 Control Automático (Lazo Cerrado)", bg="#f1f8e9",
                 font=("Arial", 13, "bold"), fg="#1b5e20").pack(pady=8)
        tk.Label(f, text="Temperatura Deseada (°C):", bg="#f1f8e9").pack()
        tk.Entry(f, textvariable=self.desired_temp_var, width=8).pack(pady=5)
        btns = tk.Frame(f, bg="#f1f8e9")
        btns.pack(pady=8)
        tk.Button(btns, text="Comenzar Lazo", width=16, bg="#81c784",
                  command=self.start_control).grid(row=0, column=0, padx=5)
        tk.Button(btns, text="Terminar Lazo", width=16, bg="#ef9a9a",
                  command=self.stop_control).grid(row=0, column=1, padx=5)

    # ---------- Funciones Manual ----------
    def _foco_temp(self):
        segundos = self.foco_t.get()
        threading.Thread(target=self._temp_thread, args=("foco", segundos), daemon=True).start()

    def _vent_temp(self):
        segundos = self.vent_t.get()
        threading.Thread(target=self._temp_thread, args=("vent", segundos), daemon=True).start()

    def _temp_thread(self, tipo, segundos):
        if tipo == "foco":
            encender_foco(True)
            self.status_var.set(f"💡 Foco ON ({segundos}s)")
        else:
            encender_ventilador(True)
            self.status_var.set(f"🌀 Ventilador ON ({segundos}s)")
        time.sleep(segundos)
        apagar_todo()
        self.status_var.set(f"{'💡' if tipo=='foco' else '🌀'} OFF (temporizado)")

    # ---------- Control Automático ----------
    def start_control(self):
        global control_thread
        with control_thread_lock:
            if control_thread and control_thread.is_alive() and not stop_control_loop.is_set():
                self.status_var.set("Control ya activo.")
                return
            stop_control_loop.clear()
            control_thread = threading.Thread(target=control_loop_fn,
                                              args=(self.root, self.desired_temp_var, self.status_var),
                                              daemon=True)
            control_thread.start()
            self.status_var.set("Lazo cerrado iniciado.")

    def stop_control(self):
        stop_control_loop.set()
        apagar_todo()
        self.status_var.set("Lazo cerrado detenido.")

    # ---------- Navegación ----------
    def hide_all(self):
        for f in (self.frame_main, self.frame_manual, self.frame_auto):
            f.pack_forget()

    def show_main(self):
        self.hide_all()
        self.frame_main.pack(fill=tk.BOTH, expand=True)

    def show_manual(self):
        self.hide_all()
        stop_control_loop.set()
        apagar_todo()
        self.frame_manual.pack(fill=tk.BOTH, expand=True)

    def show_auto(self):
        self.hide_all()
        self.frame_auto.pack(fill=tk.BOTH, expand=True)

    # ---------- Cierre seguro ----------
    def on_close(self):
        stop_temp_updater.set()
        stop_control_loop.set()
        apagar_todo()
        time.sleep(0.5)
        self.root.destroy()

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    root = tk.Tk()
    app = InvernaderoApp(root)
    root.mainloop()
