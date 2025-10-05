import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
import time
import sys

# 🔧 Configura la IP del ESP32 (cambia por la tuya)
ESP32_IP = "http://10.14.229.20"  # <-- cambia por la IP real del ESP32

# =====================================================
# Funciones de control hacia el ESP32
# =====================================================
def enviar_comando(ruta):
    try:
        requests.get(f"{ESP32_IP}{ruta}", timeout=2)
    except Exception as e:
        print(f"Error enviando comando {ruta}: {e}")

def apagar_todo():
    """Apaga todos los actuadores"""
    enviar_comando("/rele/off")
    enviar_comando("/fan/off")

def leer_temperatura():
    """Lee la temperatura actual"""
    try:
        r = requests.get(f"{ESP32_IP}/temperatura/value", timeout=2)
        if r.status_code == 200:
            valor = r.text.strip()
            try:
                return float(valor)
            except:
                return None
        else:
            return None
    except:
        return None

# =====================================================
# Pantalla de lazo abierto
# =====================================================
def lazo_abierto(root):
    ventana = tk.Toplevel(root)
    ventana.title("Control en Lazo Abierto")
    ventana.geometry("400x350")
    ventana.configure(bg="#1e1e1e")

    lbl_temp = tk.Label(ventana, text="Temperatura: -- °C", font=("DS-Digital", 30), fg="lime", bg="#1e1e1e")
    lbl_temp.pack(pady=20)

    frame_botones = tk.Frame(ventana, bg="#1e1e1e")
    frame_botones.pack(pady=10)

    # -------- Funciones de control --------
    def encender_focos():
        # Apaga ventiladores antes
        enviar_comando("/fan/off")
        time.sleep(0.2)
        enviar_comando("/rele/on")
        messagebox.showinfo("Acción", "Focos encendidos (ventiladores apagados).")

    def apagar_focos():
        enviar_comando("/rele/off")
        messagebox.showinfo("Acción", "Focos apagados.")

    def encender_ventiladores():
        # Apaga focos antes
        enviar_comando("/rele/off")
        time.sleep(0.2)
        enviar_comando("/fan/on")
        messagebox.showinfo("Acción", "Ventiladores encendidos (focos apagados).")

    def apagar_ventiladores():
        enviar_comando("/fan/off")
        messagebox.showinfo("Acción", "Ventiladores apagados.")

    ttk.Button(frame_botones, text="Encender Focos", command=encender_focos).grid(row=0, column=0, padx=5, pady=5)
    ttk.Button(frame_botones, text="Apagar Focos", command=apagar_focos).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(frame_botones, text="Encender Ventiladores", command=encender_ventiladores).grid(row=1, column=0, padx=5, pady=5)
    ttk.Button(frame_botones, text="Apagar Ventiladores", command=apagar_ventiladores).grid(row=1, column=1, padx=5, pady=5)

    # Temporizador
    ttk.Label(ventana, text="Temporizador (segundos):", background="#1e1e1e", foreground="white").pack()
    entry_tiempo = ttk.Entry(ventana)
    entry_tiempo.pack()

    def activar_temporizador():
        try:
            t = int(entry_tiempo.get())
            encender_focos()
            ventana.after(t * 1000, apagar_focos)
        except:
            messagebox.showerror("Error", "Ingrese un valor válido.")

    ttk.Button(ventana, text="Activar Temporizador", command=activar_temporizador).pack(pady=5)

    # Actualización continua de temperatura
    def actualizar_temp():
        while True:
            temp = leer_temperatura()
            if temp is not None:
                lbl_temp.config(text=f"Temperatura: {temp:.1f} °C")
            else:
                lbl_temp.config(text="Temperatura: ---")
            time.sleep(2)

    threading.Thread(target=actualizar_temp, daemon=True).start()

# =====================================================
# Pantalla de lazo cerrado
# =====================================================
def lazo_cerrado(root):
    ventana = tk.Toplevel(root)
    ventana.title("Control en Lazo Cerrado")
    ventana.geometry("400x350")
    ventana.configure(bg="#1e1e1e")

    lbl_temp = tk.Label(ventana, text="Temperatura: -- °C", font=("DS-Digital", 30), fg="cyan", bg="#1e1e1e")
    lbl_temp.pack(pady=20)

    ttk.Label(ventana, text="Temperatura deseada:", background="#1e1e1e", foreground="white").pack()
    entry_deseada = ttk.Entry(ventana)
    entry_deseada.pack(pady=5)

    lbl_estado = tk.Label(ventana, text="Estado: ---", bg="#1e1e1e", fg="white")
    lbl_estado.pack(pady=10)

    def control_automatico():
        while True:
            temp = leer_temperatura()
            if temp is not None:
                lbl_temp.config(text=f"Temperatura: {temp:.1f} °C")
                try:
                    deseada = float(entry_deseada.get())
                    if temp > deseada + 1:
                        enviar_comando("/rele/off")
                        enviar_comando("/fan/on")
                        lbl_estado.config(text="Estado: Enfriando (ventiladores ON)", fg="cyan")
                    elif temp < deseada - 1:
                        enviar_comando("/fan/off")
                        enviar_comando("/rele/on")
                        lbl_estado.config(text="Estado: Calentando (focos ON)", fg="orange")
                    else:
                        enviar_comando("/fan/off")
                        enviar_comando("/rele/off")
                        lbl_estado.config(text="Estado: Estable", fg="lime")
                except:
                    lbl_estado.config(text="Ingrese temperatura deseada", fg="red")
            time.sleep(2)

    threading.Thread(target=control_automatico, daemon=True).start()

# =====================================================
# Pantalla principal
# =====================================================
def main():
    root = tk.Tk()
    root.title("Sistema de Invernadero - ESP32")
    root.geometry("400x250")
    root.configure(bg="#1e1e1e")

    tk.Label(root, text="CONTROL DE INVERNADERO", font=("Arial", 16, "bold"), fg="white", bg="#1e1e1e").pack(pady=20)

    ttk.Button(root, text="Control en Lazo Abierto", command=lambda: lazo_abierto(root)).pack(pady=10)
    ttk.Button(root, text="Control en Lazo Cerrado", command=lambda: lazo_cerrado(root)).pack(pady=10)

    # Evento al cerrar la ventana → apaga todo
    def on_close():
        apagar_todo()
        root.destroy()
        sys.exit()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
