import tkinter as tk
from tkinter import ttk, messagebox
# Intentamos importar PIL (Pillow) para la generación de imágenes
try:
    from PIL import Image, ImageDraw
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False
    print("ADVERTENCIA: La librería 'Pillow' (PIL) no está instalada. La función de generar imagen no funcionará. Instálela con 'pip install Pillow'.")

# --- CONFIGURACIÓN ---
LIMITE_CINTA_VISUAL = 30    # Límite de caracteres para la visualización gráfica en Tkinter (animación)
LIMITE_CINTA_IMAGEN = 500   # Límite MÁXIMO de celdas a dibujar horizontalmente en la imagen
LIMITE_PASOS_IMAGEN = 5000  # Límite MÁXIMO de pasos (filas) a dibujar verticalmente en la imagen
PIXEL_SIZE = 2              # Tamaño de cada celda en la imagen final (2x2 píxeles)

# --- FUNCIÓN DE SIMULACIÓN ---

def maquina_turing(archivo_entrada = "entrada.txt", archivo_salida = "salida.txt"):
    """
    Simula la Máquina de Turing para el lenguaje L = {0^n 1^n | n >= 1}.
    Genera un archivo de log con todos los pasos.
    """
    
    # 1. LECTURA DEL ARCHIVO DE ENTRADA
    try:
        with open(archivo_entrada, 'r') as archivo:
            cadena_entrada = archivo.readline().strip()
            cinta = list(cadena_entrada)
    except FileNotFoundError:
        print(f"Error: El archivo de entrada {archivo_entrada} no se encontró")
        return

    estado = '0'
    i = 0
    paso = 0
    resultado_final = ""

    # 2. BUCLE DE SIMULACIÓN Y REGISTRO EN EL LOG
    try:
        # Abrimos el archivo de salida en modo escritura ('w')
        with open(archivo_salida, 'w') as log_file:
            log_file.write("Paso | Estado | Cabezal | Cinta\n")

            while estado != '4':
                
                # 2a. MANEJO DE LÍMITES DE LA CINTA (Símbolo Blanco 'B')
                simbolo_leido = "" 

                if i < 0:
                    cinta.insert(0, 'B')
                    i = 0
                    simbolo_leido = cinta[i]
                elif i >= len(cinta):
                    simbolo_leido = 'B'
                else:
                    simbolo_leido = cinta[i]

                # 2b. REGISTRO EN EL ARCHIVO LOG ANTES DE LA TRANSICIÓN
                cinta_str = "".join(cinta)
                log_file.write(f"{paso:02d} | {estado} | {i:02d} | {cinta_str}\n")
                
                paso += 1
                
                # 2c. LÓGICA DE TRANSICIONES
                nuevo_estado = estado
                
                # Estado 0
                if estado == '0':
                    if simbolo_leido == '0':
                        nuevo_estado = '1'
                        cinta[i] = 'X'
                        i += 1
                    elif simbolo_leido == 'Y':
                        nuevo_estado = '3'
                        cinta[i] = 'Y'
                        i += 1
                    else:
                        resultado_final = f"RECHAZO (E0): Leyó '{simbolo_leido}' inesperado."
                        break
                
                # Estado 1
                elif estado == '1':
                    if simbolo_leido == '0':
                        nuevo_estado = '1'
                        cinta[i] = '0'
                        i += 1
                    elif simbolo_leido == '1':
                        nuevo_estado = '2'
                        cinta[i] = 'Y'
                        i -= 1
                    elif simbolo_leido == 'Y':
                        nuevo_estado = '1'
                        cinta[i] = 'Y'
                        i += 1
                    else:
                        resultado_final = f"RECHAZO (E1): Leyó '{simbolo_leido}' inesperado."
                        break

                # Estado 2
                elif estado == '2':
                    if simbolo_leido == '0':
                        nuevo_estado = '2'
                        cinta[i] = '0'
                        i -= 1
                    elif simbolo_leido == 'X':
                        nuevo_estado = '0'
                        cinta[i] = 'X'
                        i += 1
                    elif simbolo_leido == 'Y':
                        nuevo_estado = '2'
                        cinta[i] = 'Y'
                        i -= 1
                    else:
                        resultado_final = f"RECHAZO (E2): Leyó '{simbolo_leido}' inesperado."
                        break

                # Estado 3
                elif estado == '3':
                    if simbolo_leido == 'Y':
                        nuevo_estado = '3'
                        cinta[i] = 'Y'
                        i += 1
                    elif simbolo_leido == 'B':
                        nuevo_estado = '4'
                        resultado_final = "ACEPTACIÓN (E4): Blanco encontrado."
                        break
                    else:
                        resultado_final = f"RECHAZO (E3): Leyó '{simbolo_leido}' inesperado."
                        break

                estado = nuevo_estado
            
            # 2d. REGISTRO FINAL FUERA DEL BUCLE
            if resultado_final.startswith("ACEPTACIÓN"):
                log_file.write(f"ACEPTACIÓN | Cinta final: {''.join(cinta)}\n")
            else:
                log_file.write(f"{resultado_final} | Cinta final: {''.join(cinta)}\n")
            
            print("-" * 30)
            print(f"*** SIMULACIÓN FINALIZADA: {resultado_final} ***")
            
    except Exception as e:
        print(f"Ocurrió un error grave durante la simulación: {str(e)}")


# --- FUNCIÓN DE VISUALIZACIÓN GRÁFICA (TKINTER) ---

def visualizar_turing(archivo_salida = "salida.txt"):
    """
    Lee el archivo de log y reproduce la simulación en una interfaz Tkinter.
    """
    try:
        with open(archivo_salida, 'r') as archivo:
            log_lines = archivo.readlines()
        
        # Filtramos solo los pasos válidos de la simulación
        log_steps = [line.strip() for line in log_lines[1:] if line.strip() and " | " in line and len(line.split(' | ')) == 4]
        
    except FileNotFoundError:
        messagebox.showerror("Error de Log", f"El archivo de log {archivo_salida} no se encontró.")
        return
    
    if not log_steps:
        messagebox.showinfo("Simulación Vacía", "El log de simulación está vacío o la máquina rechazó inmediatamente.")
        return

    # Determinamos la longitud inicial de la cinta para el límite
    try:
        initial_tape_length = len(log_steps[0].split(" | ")[3].strip())
    except:
        initial_tape_length = 0

    is_too_long = initial_tape_length > LIMITE_CINTA_VISUAL

    root = tk.Tk()
    root.title("Máquina de Turing | Simulador 0ⁿ1ⁿ")
    root.configure(bg='#282c34')

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TLabel', background='#282c34', foreground='#61dafb', font=('Consolas', 12))
    style.configure('TButton', font=('Consolas', 12, 'bold'), padding=10)

    ttk.Label(root, text="SIMULACIÓN MÁQUINA DE TURING", font=("Consolas", 18, "bold"), foreground='#FFFFFF').pack(pady=15)

    cinta_frame = ttk.Frame(root, relief=tk.RAISED, borderwidth=4)
    cinta_frame.pack(padx=10, pady=20)
    
    estado_var = tk.StringVar(root, value="Estado: 0")
    ttk.Label(root, textvariable=estado_var, font=("Consolas", 14, "bold"), foreground='#a9f30b').pack(pady=5)

    paso_var = tk.StringVar(root, value="Paso: 00")
    ttk.Label(root, textvariable=paso_var, font=("Consolas", 12)).pack(pady=5)

    # Mostrar mensaje si la cinta es demasiado larga
    if is_too_long:
        ttk.Label(cinta_frame, 
                  text=f"Cinta demasiado larga ({initial_tape_length} chars).\nLímite de visualización: {LIMITE_CINTA_VISUAL} chars.\n\nEl proceso completo se guarda en 'proceso_mt.png'.", 
                  font=('Consolas', 14), 
                  foreground='red', 
                  background='#282c34', 
                  padding=20).pack()
        # No continuamos con la animación paso a paso
        return

    # --- LÓGICA DE DIBUJO DE CINTA ---
    def draw_tape(cinta_str, cabezal_pos):
        for widget in cinta_frame.winfo_children():
            widget.destroy()
        
        for index, symbol in enumerate(cinta_str):
            bg_color = '#3c3f41' 
            fg_color = '#FFFFFF'
            
            if index == cabezal_pos:
                bg_color = '#e06c75'
                fg_color = '#282c34'
            
            label = tk.Label(
                cinta_frame,
                text=symbol,
                background=bg_color,
                foreground=fg_color,
                font=('Consolas', 18, 'bold'),
                width=3, 
                height=1,
                relief=tk.RIDGE
            )
            label.grid(row=0, column=index, padx=1, pady=1)

    # --- LÓGICA DE ANIMACIÓN ---
    current_step = 0
    is_paused = False
    
    def toggle_pause():
        nonlocal is_paused
        is_paused = not is_paused
        if is_paused:
            pause_button.config(text="Reanudar")
        else:
            pause_button.config(text="Pausar")
            next_step()

    def next_step():
        nonlocal current_step

        if is_paused:
            return

        if current_step < len(log_steps):
            line = log_steps[current_step]
            
            try:
                parts = line.split(" | ")
                paso_num = parts[0].strip()
                estado = parts[1].strip()
                cabezal = int(parts[2].strip())
                cinta_str = parts[3].strip()

                paso_var.set(f"Paso: {paso_num}")
                simbolo = cinta_str[cabezal] if cabezal < len(cinta_str) else 'B'
                estado_var.set(f"Estado: {estado} | Leyendo '{simbolo}' en Pos. {cabezal}")

                draw_tape(cinta_str, cabezal)
                current_step += 1
                root.after(500, next_step)
                start_button.config(state=tk.DISABLED)
            
            except Exception as e:
                messagebox.showerror("Error de Log", f"Error al procesar línea: {e}")
                
        else:
            # Fin de la animación
            estado_var.set("SIMULACIÓN FINALIZADA")
            final_status = log_lines[-1].strip()
            
            color = 'green' if final_status.startswith("ACEPTACIÓN") else 'red'
            
            ttk.Label(root, text=final_status, font=('Consolas', 16, 'bold'), foreground=color).pack(pady=10)
            start_button.config(text="Terminada", state=tk.DISABLED)
            pause_button.config(state=tk.DISABLED)


    # Botones de control
    control_frame = ttk.Frame(root)
    control_frame.pack(pady=20)
    
    start_button = ttk.Button(control_frame, text="Iniciar Simulación", command=next_step)
    start_button.grid(row=0, column=0, padx=10)

    pause_button = ttk.Button(control_frame, text="Pausar", command=toggle_pause, state=tk.DISABLED if is_too_long else tk.NORMAL)
    pause_button.grid(row=0, column=1, padx=10)


    root.mainloop()


# --- FUNCIÓN DE GENERACIÓN DE IMAGEN (PIXEL MAP) ---

def generar_imagen_proceso(archivo_salida="salida.txt", nombre_archivo="proceso_mt.png"):
    """
    Genera una imagen PNG que representa visualmente el historial de la cinta
    como un mapa de píxeles (tipo degradado), usando una paleta de azules y esmeraldas.
    Aplica límites de recursos y una ventana deslizante para evitar errores de memoria.
    """
    if not PIL_DISPONIBLE:
        print("No se puede generar la imagen. La librería Pillow no está disponible.")
        return

    try:
        with open(archivo_salida, 'r') as f:
            log_lines = f.readlines()

        # 1. Obtener los datos relevantes: (cinta_str, cabezal_pos) y aplicar límite de pasos
        all_steps_data = []
        max_cabezal_pos = 0 
        
        for line in log_lines[1:]:
            parts = line.strip().split(' | ')
            if len(parts) == 4:
                try:
                    # parts[2] is Cabezal (i), parts[3] is Cinta string
                    cabezal = int(parts[2].strip()) 
                    cinta_str = parts[3].strip()
                    
                    all_steps_data.append((cinta_str, cabezal))
                    
                    # Rastrear la posición máxima del cabezal para determinar el ancho total activo
                    max_cabezal_pos = max(max_cabezal_pos, cabezal)
                except ValueError:
                    continue 

        if not all_steps_data:
            print("No hay pasos de simulación para generar la imagen.")
            return

        # Aplicar el límite de pasos (altura)
        steps_to_draw = all_steps_data[:LIMITE_PASOS_IMAGEN] 
        
        if len(all_steps_data) > LIMITE_PASOS_IMAGEN:
            print(f"ADVERTENCIA: Se truncaron {len(all_steps_data) - LIMITE_PASOS_IMAGEN} pasos para la imagen (Límite: {LIMITE_PASOS_IMAGEN}).")

        
        # 2. Determinar la ventana de visualización horizontal
        
        # Ancho total de la cinta que se llegó a usar (desde el índice 0 hasta el cabezal más lejano + 1)
        # Usamos el máximo entre la longitud de la cinta más larga y la posición del cabezal más lejano
        full_required_width = max(max(len(c[0]) for c in steps_to_draw), max_cabezal_pos + 1)

        # La columna inicial para dibujar (offset) y el ancho de la imagen (max_len)
        start_col = 0
        max_len = full_required_width

        # Si el ancho total requerido excede el límite de la imagen (activamos la ventana deslizante):
        if full_required_width > LIMITE_CINTA_IMAGEN:
            # 2a. Truncar el ancho de la imagen al límite
            max_len = LIMITE_CINTA_IMAGEN 
            
            # 2b. Calcular la columna de inicio (slice) para centrar la actividad.
            # Asegura que el punto de actividad más a la derecha (max_cabezal_pos)
            # se muestre completamente, con un margen de 10 celdas a la derecha.
            start_col = max(0, max_cabezal_pos - LIMITE_CINTA_IMAGEN + 10) 
            
            print(f"ADVERTENCIA: Se truncó el ancho de la cinta a {LIMITE_CINTA_IMAGEN} celdas. La visualización comienza en la columna {start_col}.")


        # 3. Parámetros de la imagen y Colores (Paleta Esmeralda/Azul)
        COLOR_FONDO = (10, 30, 30)       
        COLOR_BLANCO = (255, 255, 255)   
        COLOR_X_ESMERALDA = (0, 150, 136) 
        COLOR_Y_AZUL_CIAN = (0, 191, 255) 
        COLOR_0_AZUL_OSCURO = (40, 80, 80) 
        COLOR_1_CIAN_MEDIO = (80, 160, 160) 

        def get_color(symbol):
            if symbol == 'X':
                return COLOR_X_ESMERALDA
            elif symbol == 'Y':
                return COLOR_Y_AZUL_CIAN
            elif symbol == 'B':
                return COLOR_BLANCO
            elif symbol == '0':
                return COLOR_0_AZUL_OSCURO
            elif symbol == '1':
                return COLOR_1_CIAN_MEDIO
            else:
                return (255, 165, 0)


        # 4. Dimensiones y Creación de la imagen
        num_pasos = len(steps_to_draw)

        ancho_img = max_len * PIXEL_SIZE
        alto_img = num_pasos * PIXEL_SIZE

        img = Image.new('RGB', (ancho_img, alto_img), COLOR_FONDO)
        draw = ImageDraw.Draw(img)

        # 5. Dibujar los píxeles (iterando sobre la ventana de ancho 'max_len')
        for paso_idx, (cinta_str, _) in enumerate(steps_to_draw):
            
            # Slice the tape string to the visible window: [start_col : start_col + max_len]
            # La porción visible de la cinta es la que va desde start_col
            cinta_limitada = cinta_str[start_col : start_col + max_len]
            
            # The drawing loop runs for the width of the image (max_len)
            for celda_idx in range(max_len):
                
                # Check if the symbol exists within the sliced tape
                if celda_idx < len(cinta_limitada):
                    simbolo = cinta_limitada[celda_idx]
                else:
                    # Si la cinta recortada es más corta que max_len, es Blanco ('B')
                    simbolo = 'B'
                    
                fill_color = get_color(simbolo)
                
                # Coordenadas del bloque de píxel (siempre relativas al borde izquierdo de la imagen)
                x1 = celda_idx * PIXEL_SIZE
                y1 = paso_idx * PIXEL_SIZE
                x2 = x1 + PIXEL_SIZE
                y2 = y1 + PIXEL_SIZE
                
                # Dibujar el rectángulo
                draw.rectangle([x1, y1, x2, y2], fill=fill_color)
                    
        # 6. Guardar la imagen
        img.save(nombre_archivo)
        print(f"\n*** Mapa de Proceso Compacto Guardado: {nombre_archivo} ***")
        
    except Exception as e:
        print(f"Ocurrió un error al generar la imagen: {str(e)}")


# --- EJECUCIÓN PRINCIPAL ---

if __name__ == "__main__":
    # La Máquina de Turing buscará 'entrada.txt'. Asegúrate de que tu generador
    # cree este archivo antes de ejecutar la simulación.

    maquina_turing()
    
    # Iniciar la visualización
    visualizar_turing()

    # Generar la imagen del proceso (si Pillow está disponible)
    generar_imagen_proceso()
