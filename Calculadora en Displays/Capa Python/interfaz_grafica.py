# Importacion de librerias

import tkinter as tk            # Interfaz grafica
from tkinter import messagebox  # Mensajes emergentes
import requests                 # Peticiones HTTP
import json                     # Manejo de JSON para historial
import os                       # Manejo de rutas y archivos
from datetime import datetime   # Manejo de fechas y horas para historial

# Configuracion Inicial

esp32_ip = "10.31.226.81"
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Directorio actual
HISTORY_FILE = os.path.join(BASE_DIR, "history.json") # Archivo de historial
NOMBRES = ["cero","uno","dos","tres","cuatro","cinco","seis","siete","ocho","nueve"]  # Nombres para display

# Funciones para comunicacion con ESP32

# Enviamos una peticion GET al ESP32 y devolvemos el resultado
def send_request(path, timeout=1.2):
    url = f"http://{esp32_ip}{path}"
    try:
        r = requests.get(url, timeout=timeout)
        return True, r.text
    except requests.exceptions.RequestException as e:
        return False, str(e)

# Diseñamos la consulta para el display especificado (decena o unidad)
def set_single_display(type_, digit):
    if digit is None or not (0 <= digit <= 9):
        return False, "Invalid digit"
    nombre = NOMBRES[digit]
    path = f"/numero/{type_}/{nombre}/on"
    return send_request(path)

# Enviamos un valor de 0 a 99 a los displays
def set_display_value(value):
    try:
        v = int(value) % 100
    except:
        return False, "invalid value"
    ok1, r1 = set_single_display("decena", v // 10)
    ok2, r2 = set_single_display("unidad", v % 10)
    return (ok1 and ok2), (r1, r2)

# Apagamos ambos displays
def clear_esp_displays():
    send_request("/numero/decena/off")
    send_request("/numero/unidad/off")

# Al comenzar cargamos el historial desde el archivo
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

# En caso de hacer nuevas operaciones guardamos el historial
def save_history(hist):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(hist, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error guardando historial:", e)

# Interfaz Grafica con Tkinter
class CalculadoraApp:

    # Definicion de la ventana principal
    def __init__(self, root):
        self.root = root
        root.title("Calculadora ESP32 - Minimalista")
        root.geometry("820x600")
        root.resizable(False, False)
        root.configure(bg="#F5E6FF")  # lavanda claro

        # Estado
        self.current_value = 0  # valor actual en display
        self.operand1 = None    # primer operando
        self.operand2 = None    # segundo operando
        self.pending_op = None  # operador pendiente
        self.input_target = 1   # 1=operand1, 2=operand2

        # Operaciones de conteo
        self.count_job = None
        self.counting = False
        self.count_dir = 1
        self.count_interval_ms = 1000

        # Cargamos historial
        self.history = load_history()

        # Creamos el display superior e inferior de la calculadora
        self.top_display_var = tk.StringVar(value="00")
        self.bottom_display_var = tk.StringVar(value="")

        # Cambiamos las propiedades del display superior (valor actual mostrado en ESP32)
        self.small_display = tk.Label(root,
                                      textvariable=self.top_display_var,
                                      font=("Segoe UI", 28, "bold"),
                                      fg="#C3F8FF", bg="#2D033B",
                                      width=6,
                                      relief="flat",
                                      bd=0,
                                      pady=10)
        self.small_display.place(x=215, y=16)

        # Cambiamos las propiedades del display inferior (operacion en curso)
        self.big_display = tk.Label(root,
                                    textvariable=self.bottom_display_var,
                                    font=("Segoe UI", 34, "bold"),
                                    fg="#FFFFFF",
                                    bg="#3B1C5C",
                                    width=12,
                                    anchor="e",
                                    pady=10)
        self.big_display.place(x=20, y=90)

        # Creamos los botones numericos y de operaciones
        self.buttons_frame = tk.Frame(root, bg="#F5E6FF")
        self.buttons_frame.place(x=20, y=180, width=480, height=360)

        # Configuracion comun para botones
        btn_cfg = {"width":6, "height":2, "font":("Segoe UI", 14), "bd":0}

        # Creamos botones numericos, los poscicionamos en una cuadricula
        digits = [
            (1, 0, 0), (2, 1, 0), (3, 2, 0),
            (4, 0, 1), (5, 1, 1), (6, 2, 1),
            (7, 0, 2), (8, 1, 2), (9, 2, 2),
            (0, 1, 3)
        ]

        # Para cada digito creamos un boton y lo posicionamos
        for val, col, row in digits:
            b = tk.Button(self.buttons_frame, text=str(val),
                          command=lambda v=val: self.on_digit(v),
                          bg="#9D4EDD", fg="white", activebackground="#7B2CBF", **btn_cfg)
            b.grid(column=col, row=row, padx=6, pady=6)

        # Botones de operaciones
        ops = ["+","-","*","/"]
        for i, sym in enumerate(ops):
            b = tk.Button(self.buttons_frame, text=sym,
                          command=lambda s=sym: self.on_operator(s),
                          bg="#7B2CBF", fg="white", activebackground="#5A189A", **btn_cfg)
            b.grid(column=3, row=i, padx=6, pady=6)

        # Botones especiales: igual y reset

        b_eq = tk.Button(self.buttons_frame, text="=", command=self.on_equals,
                         bg="#52B788", fg="white", activebackground="#40916C", **btn_cfg)
        b_eq.grid(column=2, row=3, padx=6, pady=6)

        b_reset = tk.Button(self.buttons_frame, text="Reset", command=self.reset_all,
                            bg="#FF6B6B", fg="white", activebackground="#E63946", **btn_cfg)
        b_reset.grid(column=0, row=3, padx=6, pady=6)

        # Creamos el frame de controles adicionales, estos almacenan contadores e historial
        self.ctrl_frame = tk.Frame(root, bd=0, bg="#EBD4FF")
        self.ctrl_frame.place(x=400, y=20, width=380, height=560)

        # Titulo del frame de controles
        tk.Label(self.ctrl_frame, text="Contadores y Historial", font=("Segoe UI",14,"bold"),
                 bg="#EBD4FF", fg="#2D033B").pack(pady=(10,15))

        # Botones de control de conteo
        btn_style = {"font":("Segoe UI", 12), "width":26, "height":2, "bd":0}

        tk.Button(self.ctrl_frame, text="▲ Iniciar ascendente",
                  command=lambda: self.start_count(1),
                  bg="#9D4EDD", fg="white", activebackground="#7B2CBF", **btn_style).pack(pady=6)
        tk.Button(self.ctrl_frame, text="▼ Iniciar descendente",
                  command=lambda: self.start_count(-1),
                  bg="#9D4EDD", fg="white", activebackground="#7B2CBF", **btn_style).pack(pady=6)
        
        # Boton para detener conteo
        tk.Button(self.ctrl_frame, text="⏹ Parar", command=self.stop_count,
                  bg="#7B2CBF", fg="white", activebackground="#5A189A", **btn_style).pack(pady=6)
        
        # Resetear los displays sin afectar la operacion en curso
        tk.Button(self.ctrl_frame, text="Reset displays (00)", command=self.reset_display_only,
                  bg="#FF6B6B", fg="white", activebackground="#E63946", **btn_style).pack(pady=6)

        # Creamos un contenedor para el intervalo de conteo
        frame_interval = tk.Frame(self.ctrl_frame, bg="#EBD4FF")
        frame_interval.pack(pady=15)

        # Mencionamos el intervalo y creamos un entry para modificarlo
        tk.Label(frame_interval, text="Intervalo (ms):", font=("Segoe UI", 11),
                 bg="#EBD4FF", fg="#2D033B").grid(column=0, row=0, padx=4)
        self.interval_entry = tk.Entry(frame_interval, width=10, justify="center", font=("Segoe UI", 11))
        self.interval_entry.insert(0, str(self.count_interval_ms))
        self.interval_entry.grid(column=1, row=0, padx=6)

        #Boton para mostrar el sidebar de historial
        self.history_btn = tk.Button(self.ctrl_frame, text="Ver Historial",
                                     command=self.toggle_history_sidebar,
                                     bg="#9D4EDD", fg="white", activebackground="#7B2CBF",
                                     font=("Segoe UI", 12), width=26, height=2, bd=0)
        self.history_btn.pack(pady=(20,0))

        # Sidebar para historial, inicialmente oculto
        self.sidebar_width = 420
        self.sidebar = tk.Frame(root, bd=0, bg="#F3E5F5")

        # Titulo del sidebar
        tk.Label(self.sidebar, text="Historial de resultados", bg="#F3E5F5",
                 font=("Segoe UI", 14, "bold"), fg="#2D033B").pack(pady=12)

        # Listbox para mostrar el historial
        self.history_listbox = tk.Listbox(self.sidebar, width=55, height=12,
                                          bg="#FFFFFF", fg="#2D033B",
                                          selectbackground="#9D4EDD",
                                          font=("Segoe UI", 11), relief="flat")
        self.history_listbox.pack(padx=12, pady=10, fill="both")


        # Contenedor para los botones de acciones
        action_frame = tk.Frame(self.sidebar, bg="#F3E5F5")
        action_frame.pack(pady=10)

        # fila: botones operando 1 y 2
        # operando 1 es para ocuparlo como primer numero
        # operando 2 es para ocuparlo como segundo numero, solo funciona si ya se selecciono el primer numero y operador
        btns_frame = tk.Frame(action_frame, bg="#F3E5F5")
        btns_frame.pack(pady=6)
        tk.Button(btns_frame, text="Operando 1", command=self.use_selected_as_operand1,
                  bg="#7B2CBF", fg="white", activebackground="#5A189A",
                  font=("Segoe UI", 11), width=14, height=2, bd=0).grid(column=0, row=0, padx=8)
        tk.Button(btns_frame, text="Operando 2", command=self.use_selected_as_operand2,
                  bg="#7B2CBF", fg="white", activebackground="#5A189A",
                  font=("Segoe UI", 11), width=14, height=2, bd=0).grid(column=1, row=0, padx=8)

        # fila: borrar y regresar
        tk.Button(action_frame, text="Borrar historial", command=self.clear_history,
                  bg="#FF6B6B", fg="white", activebackground="#E63946",
                  font=("Segoe UI", 12), width=28, height=2, bd=0).pack(pady=6)

        tk.Button(action_frame, text="Regresar", command=self.toggle_history_sidebar,
                  bg="#9D4EDD", fg="white", activebackground="#7B2CBF",
                  font=("Segoe UI", 12), width=28, height=2, bd=0).pack(pady=6)


        # Inicializamos el display y el historial
        self.update_top_display(00, send_to_esp=True)
        self.refresh_history_listbox()
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    # Funcion para actualizar el display superior y enviar el valor al ESP32
    def update_top_display(self, value, send_to_esp=True):
        try:
            v = int(value)
        except:
            v = 0
        v = v % 100
        self.current_value = v
        self.top_display_var.set(f"{v:02d}")
        if send_to_esp:
            ok, resp = set_display_value(v)
            if not ok:
                print("No se pudo enviar display al ESP32:", resp)
        return v

    # Funcion para manejar la entrada de digitos y operadores
    def on_digit(self, d):
        if self.input_target == 1:
            if self.operand1 is None:
                self.operand1 = d
            elif self.operand1 < 10:
                self.operand1 = self.operand1 * 10 + d
        else:
            if self.operand2 is None:
                self.operand2 = d
            elif self.operand2 < 10:
                self.operand2 = self.operand2 * 10 + d
        self._refresh_big_display()

    # Si se presiona un operador, se guarda el operando actual y se prepara para el siguiente
    def on_operator(self, op):
        if self.operand1 is None:
            self.operand1 = self.current_value
        self.pending_op = op
        self.input_target = 2
        self._refresh_big_display()

    # Cuando se presiona igual, se realiza la operacion y se actualiza el display
    def on_equals(self):
        if self.operand1 is None or self.pending_op is None or self.operand2 is None:
            return
        a, b = self.operand1, self.operand2
        res = 0
        try:
            if self.pending_op == "+": res = a + b
            elif self.pending_op == "-": res = a - b
            elif self.pending_op == "*": res = a * b
            elif self.pending_op == "/":
                if b == 0:
                    messagebox.showwarning("Advertencia", "División por cero no permitida.")
                    self._clear_operation_inputs()
                    self.bottom_display_var.set("")
                    return
                res = int(a / b)
        except Exception as e:
            print("Error:", e)
            res = 0
        if res < 0 or res > 99:
            messagebox.showwarning("Advertencia", "Resultado fuera de rango (0–99).")
            self._clear_operation_inputs()
            self.bottom_display_var.set("")
            return
        self.update_top_display(res, send_to_esp=True)
        op_text = f"{a} {self.pending_op} {b} ="
        self.add_to_history(res, operation=op_text)
        self.bottom_display_var.set(op_text)
        self._clear_operation_inputs(keep_big_display=True)

    # Actualiza el display grande con la operacion en curso
    def _refresh_big_display(self):
        left = "" if self.operand1 is None else str(self.operand1)
        mid = f" {self.pending_op} " if self.pending_op else ""
        right = "" if self.operand2 is None else str(self.operand2)
        self.bottom_display_var.set(f"{left}{mid}{right}")

    # Limpia los operandos y el operador pendiente
    def _clear_operation_inputs(self, keep_big_display=False):
        self.operand1 = None
        self.operand2 = None
        self.pending_op = None
        self.input_target = 1
        if not keep_big_display:
            self.bottom_display_var.set("")

    # Resetea solo los displays sin afectar la operacion en curso
    def reset_display_only(self):
        self.update_top_display(0, send_to_esp=True)
        clear_esp_displays()
    
    # Resetea todo, incluyendo la operacion en curso
    def reset_all(self):
        self._clear_operation_inputs()
        self.bottom_display_var.set("")
        self.update_top_display(00, send_to_esp=True)
        clear_esp_displays()

    # Funcion para iniciar el conteo ascendente o descendente
    def start_count(self, direction):
        try:
            v = int(self.interval_entry.get())
            if v < 50: v = 50
            self.count_interval_ms = v
        except: self.count_interval_ms = 1000
        self.count_dir = 1 if direction >= 0 else -1
        if not self.counting:
            self.counting = True
            self._count_step()

    # Funcion interna para realizar un paso de conteo y programar el siguiente
    def _count_step(self):
        if not self.counting: return
        new = (self.current_value + self.count_dir) % 100
        self.update_top_display(new, send_to_esp=True)
        self.add_to_history(new, operation=("COUNT_UP" if self.count_dir == 1 else "COUNT_DOWN"))
        self.count_job = self.root.after(self.count_interval_ms, self._count_step)

    # Funcion para detener el conteo
    def stop_count(self):
        if self.counting and self.count_job:
            try: self.root.after_cancel(self.count_job)
            except: pass
        self.count_job = None
        self.counting = False

    # Metodo para manejar el historial, agrega entradas y actualiza la lista
    def add_to_history(self, value, operation=None):
        entry = {"value": int(value), "display": f"{int(value)%100:02d}",
                 "operation": operation or "", "ts": datetime.now().isoformat()}
        self.history.insert(0, entry)
        if len(self.history) > 2000: self.history = self.history[:2000]
        save_history(self.history)
        self.refresh_history_listbox()

    # Actualiza el Listbox del historial con las entradas actuales
    def refresh_history_listbox(self):
        self.history_listbox.delete(0, tk.END)
        for h in self.history:
            ts = h.get("ts","")[:19].replace("T"," ")
            op = h.get("operation","")
            disp = h.get("display","00")
            text = f"{ts} | {disp} | {op}"
            self.history_listbox.insert(tk.END, text)

    # Muestra u oculta el sidebar de historial
    def toggle_history_sidebar(self):
        if self.sidebar in self.root.place_slaves():
            self.sidebar.place_forget()
        else:
            self.sidebar.place(x=400, y=0, width=420, height=600)
            self.refresh_history_listbox()

    # Obtiene la entrada seleccionada en el Listbox del historial
    def get_selected_history_entry(self):
        sel = self.history_listbox.curselection()
        if not sel: return None
        idx = sel[0]
        if idx < 0 or idx >= len(self.history): return None
        return self.history[idx]

    # Usa la entrada seleccionada como operando 1 o 2 segun corresponda
    def use_selected_as_operand1(self):
        entry = self.get_selected_history_entry()
        if not entry: return
        value = int(entry.get("value", 0)) % 100
        self.operand1 = value
        self.input_target = 2 if self.pending_op else 1
        self._refresh_big_display()

    # Usa la entrada seleccionada como operando 2, requiere que ya se haya seleccionado operando 1 y operador
    def use_selected_as_operand2(self):
        entry = self.get_selected_history_entry()
        if not entry: return
        value = int(entry.get("value", 0)) % 100
        if self.pending_op is None:
            messagebox.showinfo("Info", "Primero selecciona un operador.")
            return
        self.operand2 = value
        self.input_target = 2
        self._refresh_big_display()

    # Borra todo el historial despues de confirmar
    def clear_history(self):
        if messagebox.askyesno("Confirmar", "¿Borrar todo el historial?"):
            self.history = []
            save_history(self.history)
            self.refresh_history_listbox()

    # Al momento de cerrar la aplicacion, guardamos el historial y apagamos displays
    def on_close(self):
        save_history(self.history)
        self.stop_count()
        try: clear_esp_displays()
        except: pass
        self.root.destroy()

# Creamos el inicio de la aplicacion
if __name__ == "__main__":
    root = tk.Tk()
    app = CalculadoraApp(root)
    root.mainloop()
