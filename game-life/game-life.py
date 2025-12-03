import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import time

class GameOfLifeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador Autómatas Celulares - Juego de la Vida")
        self.root.geometry("1400x900")

        # --- Parámetros Iniciales ---
        self.rows = 500
        self.cols = 500
        self.cell_size = 2  # Pixeles por célula
        self.zoom_level = 1.0
        self.running = False
        self.toroidal = False # False = Frontera Nula, True = Toro
        self.show_patterns = False # Ahora activa el modo "Visualizar Edad"
        
        # Reglas (Default Conway: B3/S23)
        self.rule_b = [3]
        self.rule_s = [2, 3]

        # --- PALETA DE COLORES (Lilas) ---
        self.color_dead = [0, 0, 0]        # Negro
        
        # Edad 1: Recién nacida (Oscuro)
        self.color_age_1 = [140, 80, 180]  
        # Edad 2: Sobreviviente (El Lila original)
        self.color_age_2 = [200, 160, 255] 
        # Edad 3+: Estable/Veterana (Brillante/Blanco)
        self.color_age_3 = [250, 230, 255]

        self.color_pattern = [255, 0, 0] # Rojo (Legacy o alertas)

        # Estadísticas
        self.generation = 0
        self.population_history = []
        self.stats_variance = []
        self.stats_mean = []

        # Inicializar Grid con ceros
        self.grid = np.zeros((self.rows, self.cols), dtype=np.uint8)

        # --- Interfaz Gráfica ---
        self.create_ui()
        
        # Inicializar gráficos de matplotlib
        self.init_plots()

        # Configurar límite de zoom inicial
        self.update_zoom_limit()

        # Render inicial
        self.update_canvas()

    def create_ui(self):
        # Panel Izquierdo (Controles)
        control_frame = tk.Frame(self.root, width=250, bg="#f0f0f0")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Título
        tk.Label(control_frame, text="Controles", font=("Arial", 14, "bold")).pack(pady=10)

        # Botones de Simulación
        btn_frame = tk.Frame(control_frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Iniciar/Pausar", command=self.toggle_simulation, bg="#dddddd").grid(row=0, column=0, padx=2)
        tk.Button(btn_frame, text="Un Paso", command=self.step_simulation, bg="#dddddd").grid(row=0, column=1, padx=2)
        tk.Button(btn_frame, text="Limpiar", command=self.clear_grid, bg="#ffcccc").grid(row=1, column=0, padx=2, pady=5)
        tk.Button(btn_frame, text="Reiniciar Stats", command=self.reset_stats, bg="#ccffcc").grid(row=1, column=1, padx=2, pady=5)

        # Configuración de Tamaño
        tk.Label(control_frame, text="Tamaño del Grid:").pack(pady=(10,0))
        size_frame = tk.Frame(control_frame)
        size_frame.pack()
        self.entry_rows = tk.Entry(size_frame, width=5)
        self.entry_rows.insert(0, "500")
        self.entry_rows.pack(side=tk.LEFT)
        tk.Label(size_frame, text="x").pack(side=tk.LEFT)
        self.entry_cols = tk.Entry(size_frame, width=5)
        self.entry_cols.insert(0, "500")
        self.entry_cols.pack(side=tk.LEFT)
        tk.Button(control_frame, text="Redimensionar", command=self.resize_grid, width=20).pack(pady=2)

        # Zoom Dinámico
        tk.Label(control_frame, text="Zoom (Célula px):").pack(pady=(10,0))
        self.zoom_slider = tk.Scale(control_frame, from_=1, to=10, orient=tk.HORIZONTAL, command=self.change_zoom)
        self.zoom_slider.set(2)
        self.zoom_slider.pack(fill=tk.X, padx=10)
        self.lbl_zoom_info = tk.Label(control_frame, text="Max Zoom: --", font=("Arial", 8))
        self.lbl_zoom_info.pack()

        # Reglas
        tk.Label(control_frame, text="Regla (Formato B/S):").pack(pady=(10,0))
        self.rule_var = tk.StringVar(value="B3/S23")
        tk.Entry(control_frame, textvariable=self.rule_var).pack()
        tk.Button(control_frame, text="Aplicar Regla", command=self.parse_rule).pack(pady=2)
        
        # Presets de Reglas
        preset_frame = tk.Frame(control_frame)
        preset_frame.pack(pady=2)
        tk.Button(preset_frame, text="Vida (Conway)", command=lambda: self.set_rule_preset("B3/S23"), fg="blue").pack(fill=tk.X)
        tk.Button(preset_frame, text="Difusión (B2/S7)", command=lambda: self.set_rule_preset("B2/S7")).pack(fill=tk.X)

        # Frontera
        self.toroidal_var = tk.BooleanVar(value=False)
        tk.Checkbutton(control_frame, text="Frontera Toro (Toroidal)", variable=self.toroidal_var, command=self.toggle_boundary).pack(pady=5)

        # Archivos
        tk.Label(control_frame, text="Archivos:").pack(pady=(10,0))
        tk.Button(control_frame, text="Guardar Estado", command=self.save_state).pack(fill=tk.X, padx=10)
        tk.Button(control_frame, text="Cargar Estado", command=self.load_state).pack(fill=tk.X, padx=10)

        # Experimentos
        tk.Label(control_frame, text="Experimentos:").pack(pady=(10,0))
        tk.Button(control_frame, text="Setup Colisión Gliders", command=self.setup_glider_experiment).pack(fill=tk.X, padx=10)

        # Estadísticas Texto
        self.lbl_stats = tk.Label(control_frame, text="Gen: 0\nPoblación: 0", font=("Consolas", 10), justify=tk.LEFT, bg="white", relief=tk.SUNKEN)
        self.lbl_stats.pack(fill=tk.X, padx=10, pady=20)

        # Panel Central (Canvas con Scroll)
        center_frame = tk.Frame(self.root)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas Container
        self.canvas_frame = tk.Frame(center_frame, bg="gray")
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="#202020", cursor="cross")
        
        # Scrollbars
        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.h_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)

        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Eventos del mouse
        self.canvas.bind("<Button-1>", self.on_canvas_click)      # Click izquierdo: Poner/Quitar
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)      # Arrastrar: Dibujar

        # Panel Derecho (Gráficos)
        self.plot_frame = tk.Frame(self.root, width=300)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

    def init_plots(self):
        # Crear figuras para matplotlib
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(4, 8), dpi=80)
        self.fig.tight_layout(pad=3.0)

        self.line1, = self.ax1.plot([], [], 'g-')
        self.ax1.set_title("Densidad Poblacional")
        self.ax1.set_xlabel("Gen")
        self.ax1.set_ylabel("Células")

        self.line2, = self.ax2.plot([], [], 'b-')
        self.ax2.set_title("Densidad (Log10)")
        self.ax2.set_xlabel("Gen")
        self.ax2.set_yscale('log')

        # Canvas de matplotlib
        self.plot_canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_plots(self):
        gens = range(len(self.population_history))
        self.line1.set_data(gens, self.population_history)
        self.line2.set_data(gens, self.population_history)
        
        self.ax1.relim()
        self.ax1.autoscale_view()
        self.ax2.relim()
        self.ax2.autoscale_view()
        
        self.plot_canvas.draw_idle()

    # --- Lógica del Juego ---

    def parse_rule(self):
        rule_str = self.rule_var.get().upper()
        try:
            # Espera formato B3/S23
            parts = rule_str.split('/')
            b_part = parts[0].replace('B', '')
            s_part = parts[1].replace('S', '')
            
            self.rule_b = [int(c) for c in b_part]
            self.rule_s = [int(c) for c in s_part]
            messagebox.showinfo("Regla Actualizada", f"Nacimiento: {self.rule_b}, Sobrevive: {self.rule_s}")
        except:
            messagebox.showerror("Error", "Formato inválido. Use Bx/Sy (Ej: B3/S23)")

    def set_rule_preset(self, rule_str):
        self.rule_var.set(rule_str)
        self.parse_rule()

    def resize_grid(self):
        try:
            r = int(self.entry_rows.get())
            c = int(self.entry_cols.get())
            
            # CAMBIO: Límite entre 50 y 1000
            if r < 50 or c < 50 or r > 1000 or c > 1000:
                raise ValueError
            self.rows = r
            self.cols = c
            self.grid = np.zeros((self.rows, self.cols), dtype=np.uint8)
            self.reset_stats()
            
            # Recalcular límite de zoom seguro
            self.update_zoom_limit()
            self.update_canvas()
            
        except ValueError:
            messagebox.showerror("Error", "Dimensiones inválidas (50-1000)")

    def update_zoom_limit(self):
        # Lógica de seguridad para 8GB RAM + User Preference:
        # - Grid >= 1000 -> Zoom Max 3
        # - Grid <= 100  -> Zoom Max 10 (Por diseño, aunque en 50x50 podrías más, lo acotamos a 10)
        
        max_dimension = max(self.rows, self.cols)
        
        if max_dimension >= 1000:
            max_allowed_zoom = 3
        elif max_dimension <= 100:
            max_allowed_zoom = 10
        else:
            # Interpolación lineal simple o budget
            # Presupuesto: 3000 pixeles de lado máximo
            max_allowed_zoom = 3000 // max_dimension
        
        # Mínimo siempre 1, Máximo absoluto 10
        max_allowed_zoom = max(1, min(10, max_allowed_zoom))
        
        # Actualizar slider
        current_zoom = self.zoom_slider.get()
        self.zoom_slider.config(to=max_allowed_zoom)
        
        if current_zoom > max_allowed_zoom:
            self.zoom_slider.set(max_allowed_zoom)
            self.cell_size = max_allowed_zoom
        
        self.lbl_zoom_info.config(text=f"Max Zoom: {max_allowed_zoom}x")

    def change_zoom(self, val):
        self.cell_size = int(val)
        self.update_canvas()

    def toggle_boundary(self):
        self.toroidal = self.toroidal_var.get()

    def step_simulation(self):
        # IMPORTANTE: self.grid ahora contiene edades (0, 1, 2, 3...)
        # Para calcular vecinos, necesitamos una versión binaria (0 = muerta, >0 = viva)
        binary_grid = (self.grid > 0).astype(np.uint8)

        if self.toroidal:
            N  = np.roll(binary_grid, -1, axis=0)
            S  = np.roll(binary_grid, 1, axis=0)
            E  = np.roll(binary_grid, -1, axis=1)
            W  = np.roll(binary_grid, 1, axis=1)
            NE = np.roll(N, -1, axis=1)
            NW = np.roll(N, 1, axis=1)
            SE = np.roll(S, -1, axis=1)
            SW = np.roll(S, 1, axis=1)
        else:
            grid_pad = np.pad(binary_grid, 1, mode='constant', constant_values=0)
            N  = grid_pad[:-2, 1:-1]
            S  = grid_pad[2:, 1:-1]
            W  = grid_pad[1:-1, :-2]
            E  = grid_pad[1:-1, 2:]
            NE = grid_pad[:-2, 2:]
            NW = grid_pad[:-2, :-2]
            SE = grid_pad[2:, 2:]
            SW = grid_pad[2:, :-2]

        neighbors = N + S + E + W + NE + NW + SE + SW

        # Reglas Vectorizadas con Edad
        # 1. Nacimiento: Estaba muerta (==0) y vecinos adecuados
        birth_mask = np.isin(neighbors, self.rule_b) & (self.grid == 0)
        
        # 2. Supervivencia: Estaba viva (>0) y vecinos adecuados
        survive_mask = np.isin(neighbors, self.rule_s) & (self.grid > 0)

        # Crear nueva grid
        next_grid = np.zeros_like(self.grid)
        
        # Nacen con edad 1
        next_grid[birth_mask] = 1 
        
        # Sobreviven y envejecen (+1)
        # Capamos la edad a 3 para no desbordar inútilmente
        next_grid[survive_mask] = self.grid[survive_mask] + 1
        next_grid[next_grid > 3] = 3

        self.grid = next_grid

        # Stats
        self.generation += 1
        pop = np.sum(binary_grid) # Sumar binario para población correcta
        self.population_history.append(pop)
        
        if pop > 0:
            indices = np.argwhere(binary_grid == 1)
            mean_pos = np.mean(indices, axis=0)
            var_pos = np.var(indices, axis=0)
            mean_val = np.mean(mean_pos)
            var_val = np.mean(var_pos)
        else:
            mean_val = 0
            var_val = 0
            
        self.stats_mean.append(mean_val)
        self.stats_variance.append(var_val)

        self.lbl_stats.config(text=f"Gen: {self.generation}\nPoblación: {pop}\nMedia Esp: {mean_val:.2f}\nVarianza: {var_val:.2f}")

        self.update_canvas()
        
        if self.generation % 5 == 0:
            self.update_plots()

    def loop(self):
        if self.running:
            delay = 10 if self.rows < 1000 else 100 
            self.root.after(delay, self.loop_step)
    
    def loop_step(self):
        if self.running:
            self.step_simulation()
            self.loop()

    def toggle_simulation(self):
        self.running = not self.running
        if self.running:
            self.loop()

    def clear_grid(self):
        self.running = False
        self.grid = np.zeros((self.rows, self.cols), dtype=np.uint8)
        self.reset_stats()
        self.update_canvas()

    def reset_stats(self):
        self.generation = 0
        self.population_history = []
        self.stats_mean = []
        self.stats_variance = []
        self.update_plots()

    # --- Manejo Gráfico (Canvas) ---

    def update_canvas(self):
        h, w = self.grid.shape
        img_array = np.zeros((h, w, 3), dtype=np.uint8)

        # Mapeo de colores según edad
        # Edad 1: Lila Oscuro
        img_array[self.grid == 1] = self.color_age_1
        # Edad 2: Lila Normal
        img_array[self.grid == 2] = self.color_age_2
        # Edad 3+: Blanco/Brillante
        img_array[self.grid >= 3] = self.color_age_3

        pil_image = Image.fromarray(img_array, mode='RGB')
        
        new_w = int(w * self.cell_size)
        new_h = int(h * self.cell_size)
        
        pil_image = pil_image.resize((new_w, new_h), Image.NEAREST)
        
        self.tk_image = ImageTk.PhotoImage(pil_image)

        self.canvas.config(scrollregion=(0, 0, new_w, new_h))
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

    def get_cell_coords(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        col = int(x / self.cell_size)
        row = int(y / self.cell_size)
        return row, col

    def on_canvas_click(self, event):
        self.on_canvas_drag(event)

    def on_canvas_drag(self, event):
        row, col = self.get_cell_coords(event)
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row, col] = 1 # Dibujar fuerza edad 1
            self.update_canvas()

    # --- Archivos ---
    def save_state(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if filename:
            # Guardamos la grilla tal cual (con edades)
            np.savetxt(filename, self.grid, fmt='%d')
            messagebox.showinfo("Info", "Guardado exitosamente")

    def load_state(self):
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filename:
            try:
                loaded_grid = np.loadtxt(filename, dtype=np.uint8)
                if loaded_grid.ndim == 2:
                    self.rows, self.cols = loaded_grid.shape
                    self.grid = loaded_grid
                    self.entry_rows.delete(0, tk.END); self.entry_rows.insert(0, str(self.rows))
                    self.entry_cols.delete(0, tk.END); self.entry_cols.insert(0, str(self.cols))
                    
                    self.update_zoom_limit() # Recalcular al cargar
                    self.update_canvas()
                    self.reset_stats()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar: {e}")

    # --- Experimentos ---
    def setup_glider_experiment(self):
        density = simpledialog.askinteger("Input", "Gliders por sitio (10, 100, 1000 aprox):", minvalue=1, maxvalue=5000)
        if not density: return
        
        self.clear_grid()
        self.set_rule_preset("B3/S23") 
        
        glider_se = np.array([[0,1,0],
                              [0,0,1],
                              [1,1,1]]) 
        
        glider_nw = np.array([[0,1,1],
                              [1,0,1],
                              [0,0,1]]) 

        for _ in range(density):
            r = np.random.randint(0, self.rows // 3)
            c = np.random.randint(0, self.cols - 5)
            try:
                self.grid[r:r+3, c:c+3] = glider_se
            except: pass
            
        for _ in range(density):
            r = np.random.randint(2 * self.rows // 3, self.rows - 5)
            c = np.random.randint(0, self.cols - 5)
            try:
                self.grid[r:r+3, c:c+3] = glider_nw
            except: pass

        self.update_canvas()
        messagebox.showinfo("Experimento", f"Configurado choque de ~{density*2} gliders.\nPresione Iniciar.")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameOfLifeApp(root)
    root.mainloop()