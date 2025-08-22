import tkinter as tk

class Semaforo:
    def __init__(self, root):
        self.root = root
        self.root.title("Semáforo")
        self.root.geometry("200x400")

        # Canvas para dibujar el semáforo
        self.canvas = tk.Canvas(root, width=200, height=300, bg="black")
        self.canvas.pack()

        # Dibujar los círculos (luces apagadas al inicio)
        self.luz_roja = self.canvas.create_oval(50, 20, 150, 100, fill="gray")
        self.luz_amarilla = self.canvas.create_oval(50, 110, 150, 190, fill="gray")
        self.luz_verde = self.canvas.create_oval(50, 200, 150, 280, fill="gray")

        # Botones de control
        frame_botones = tk.Frame(root)
        frame_botones.pack(pady=10)

        tk.Button(frame_botones, text="Rojo", command=lambda: self.encender(["rojo"])) .grid(row=0, column=0, padx=5)
        tk.Button(frame_botones, text="Amarillo", command=lambda: self.encender(["amarillo"])) .grid(row=0, column=1, padx=5)
        tk.Button(frame_botones, text="Verde", command=lambda: self.encender(["verde"])) .grid(row=0, column=2, padx=5)
        tk.Button(frame_botones, text="Todos", command=lambda: self.encender(["rojo", "amarillo", "verde"])) .grid(row=1, column=1, pady=5)

    def encender(self, luces):
        # Apagar todas
        self.canvas.itemconfig(self.luz_roja, fill="gray")
        self.canvas.itemconfig(self.luz_amarilla, fill="gray")
        self.canvas.itemconfig(self.luz_verde, fill="gray")

        # Encender las seleccionadas
        if "rojo" in luces:
            self.canvas.itemconfig(self.luz_roja, fill="red")
        if "amarillo" in luces:
            self.canvas.itemconfig(self.luz_amarilla, fill="yellow")
        if "verde" in luces:
            self.canvas.itemconfig(self.luz_verde, fill="green")

# Ejecutar ventana principal
if __name__ == "__main__":
    root = tk.Tk()
    app = Semaforo(root)
    root.mainloop()