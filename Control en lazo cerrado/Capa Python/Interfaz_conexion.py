import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import time

# ============================
# CONFIGURACIÓN DE CONEXIONES
# ============================

ESP_INVERNADERO = "http://10.14.229.20"   # IP del ESP32 del invernadero
ESP_DISPLAY = "http://10.14.229.81"       # IP del ESP32 del display 7 segmentos

# ============================
# FUNCIONES BASE
# ============================

def obtener_temperatura():
    """Obtiene la temperatura actual desde el ESP32 del invernadero"""
    try:
        r = requests.get(f"{ESP_INVERNADERO}/temperatura/value", timeout=5)
        if r.status_code == 200:
            return float(r.text.strip())
    except:
        return None
    return None


def numero_a_nombre(num):
    """Convierte número a texto para URLs del display"""
    nombres = ["cero","uno","dos","tres","cuatro","cinco","seis","siete","ocho","nueve"]
    return nombres[num]


def mostrar_en_display(temperatura):
    """Muestra solo los enteros en el display 7 segmentos (sin redondear)"""
    try:
        temperatura_entera = int(temperatura)
        decenas = temperatura_entera // 10
        unidades = temperatura_entera % 10

        # Apagar antes de actualizar
        requests.get(f"{ESP_DISPLAY}/numero/unidad/off", timeout=3)
        requests.get(f"{ESP_DISPLAY}/numero/decena/off", timeout=3)

        # Mostrar decenas y unidades
        requests.get(f"{ESP_DISPLAY}/numero/decena/{numero_a_nombre(decenas)}/on", timeout=3)
        requests.get(f"{ESP_DISPLAY}/numero/unidad/{numero_a_nombre(unidades)}/on", timeout=3)
    except Exception as e:
        print("Error al mostrar en display:", e)


def apagar_todo():
    """Apaga los actuadores al cerrar el programa"""
    try:
        requests.get(f"{ESP_INVERNADERO}/rele/off", timeout=3)
        requests.get(f"{ESP_INVERNADERO}/fan/off", timeout=3)
    except:
        pass


# ============================
# CLASE PRINCIPAL DE LA INTERFAZ
# ============================

class InvernaderoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Invernadero")
        self.root.geometry("400x350")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        ttk.Label(root, text="Seleccione modo de control:", font=("Arial", 12)).pack(pady=10)
        ttk.Button(root, text="Lazo Abierto", command=self.lazo_abierto).pack(pady=5)
        ttk.Button(root, text="Lazo Cerrado", command=self.lazo_cerrado).pack(pady=5)

        self.actualizando = True
        self.hilo_temperatura = threading.Thread(target=self.actualizar_temperatura, daemon=True)
        self.hilo_temperatura.start()

    # --------- Mostrar Temperatura en Display y GUI ---------
    def actualizar_temperatura(self):
        while self.actualizando:
            temp = obtener_temperatura()
            if temp is not None:
                mostrar_en_display(temp)  # Mostrar solo enteros en display
            time.sleep(5)

    # --------- Modo Lazo Abierto ---------
    def lazo_abierto(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Lazo Abierto")
        ventana.geometry("400x350")

        temp_label = ttk.Label(ventana, text="Temperatura actual: -- °C", font=("Arial", 12))
        temp_label.pack(pady=10)

        def actualizar_temp():
            temp = obtener_temperatura()
            if temp is not None:
                temp_label.config(text=f"Temperatura actual: {temp:.2f} °C")
                mostrar_en_display(temp)
            ventana.after(3000, actualizar_temp)

        def encender_foco():
            apagar_ventilador()
            requests.get(f"{ESP_INVERNADERO}/rele/on")

        def apagar_foco():
            requests.get(f"{ESP_INVERNADERO}/rele/off")

        def encender_ventilador():
            apagar_foco()
            requests.get(f"{ESP_INVERNADERO}/fan/on")

        def apagar_ventilador():
            requests.get(f"{ESP_INVERNADERO}/fan/off")

        ttk.Button(ventana, text="Encender Foco", command=encender_foco).pack(pady=5)
        ttk.Button(ventana, text="Apagar Foco", command=apagar_foco).pack(pady=5)
        ttk.Button(ventana, text="Encender Ventilador", command=encender_ventilador).pack(pady=5)
        ttk.Button(ventana, text="Apagar Ventilador", command=apagar_ventilador).pack(pady=5)

        actualizar_temp()

    # --------- Modo Lazo Cerrado ---------
    def lazo_cerrado(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Lazo Cerrado")
        ventana.geometry("400x350")

        ttk.Label(ventana, text="Temperatura deseada:", font=("Arial", 11)).pack(pady=5)
        entrada_temp = ttk.Entry(ventana)
        entrada_temp.pack(pady=5)

        lbl_actual = ttk.Label(ventana, text="Temperatura actual: -- °C", font=("Arial", 11))
        lbl_actual.pack(pady=5)

        def controlar():
            temp_deseada = entrada_temp.get()
            if not temp_deseada:
                messagebox.showwarning("Error", "Ingrese una temperatura deseada")
                return
            try:
                temp_deseada = float(temp_deseada)
            except:
                messagebox.showwarning("Error", "Temperatura inválida")
                return

            def control_loop():
                while True:
                    temp_actual = obtener_temperatura()
                    if temp_actual is not None:
                        lbl_actual.config(text=f"Temperatura actual: {temp_actual:.2f} °C")
                        mostrar_en_display(temp_actual)

                        if temp_actual < temp_deseada:
                            # Encender foco (calentar)
                            requests.get(f"{ESP_INVERNADERO}/rele/on")
                            requests.get(f"{ESP_INVERNADERO}/fan/off")
                        else:
                            # Encender ventilador (enfriar)
                            requests.get(f"{ESP_INVERNADERO}/rele/off")
                            requests.get(f"{ESP_INVERNADERO}/fan/on")
                    time.sleep(5)

            threading.Thread(target=control_loop, daemon=True).start()

        ttk.Button(ventana, text="Iniciar Control", command=controlar).pack(pady=10)

    def on_close(self):
        """Apagar todo al cerrar la app"""
        self.actualizando = False
        apagar_todo()
        self.root.destroy()

# ============================
# EJECUCIÓN PRINCIPAL
# ============================

if __name__ == "__main__":
    root = tk.Tk()
    app = InvernaderoApp(root)
    root.mainloop()
