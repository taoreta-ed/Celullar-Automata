import tkinter as tk
from tkinter import ttk, messagebox
# Intentamos importar PIL (Pillow) para la generación de imágenes
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False
    print("ADVERTENCIA: La librería 'Pillow' (PIL) no está instalada. La función de generar imagen no funcionará. Instálela con 'pip install Pillow'.")

# --- CONFIGURACIÓN ---
LIMITE_CINTA_VISUAL = 30 # Límite de caracteres para la visualización gráfica en Tkinter

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
                
                # print(f"Paso {paso:02d}: E{estado} lee '{simbolo_leido}' en pos. {i:02d}. Cinta: {cinta_str}")
                
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
    # (Usamos el primer paso válido)
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
                  text=f"Cinta demasiado larga ({initial_tape_length} chars).\nLímite de visualización: {LIMITE_CINTA_VISUAL} chars.", 
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


# --- FUNCIÓN DE GENERACIÓN DE IMAGEN (PIL) ---

def generar_imagen_proceso(archivo_salida="salida.txt", nombre_archivo="proceso_mt.png"):
    """
    Genera una imagen PNG que representa visualmente el historial de la cinta.
    """
    if not PIL_DISPONIBLE:
        print("No se puede generar la imagen. La librería Pillow no está disponible.")
        return

    try:
        with open(archivo_salida, 'r') as f:
            log_lines = f.readlines()

        # CORRECCIÓN: Filtrar líneas para asegurar que tienen 4 partes (Paso, Estado, Cabezal, Cinta)
        cintas = []
        for line in log_lines[1:]:
            parts = line.strip().split(' | ')
            if len(parts) == 4:
                cintas.append(parts[3].strip())
        
        if not cintas:
            print("No hay pasos de simulación para generar la imagen.")
            return

        # 1. Parámetros de la imagen
        alto_celda = 20
        ancho_celda = 20
        margen = 10
        
        max_len = max(len(c) for c in cintas)
        num_pasos = len(cintas)

        # Dimensiones de la imagen
        ancho_img = max_len * ancho_celda + 2 * margen
        alto_img = num_pasos * alto_celda + 2 * margen 

        # Colores
        COLOR_FONDO = (20, 20, 30)
        COLOR_BLANCO = (255, 255, 255)
        COLOR_X_AZUL = (0, 102, 204)
        COLOR_Y_VERDE = (0, 153, 51)
        COLOR_0_GRIS = (100, 100, 100)
        COLOR_1_GRIS = (150, 150, 150)

        # 2. Crear la imagen
        img = Image.new('RGB', (ancho_img, alto_img), COLOR_FONDO)
        draw = ImageDraw.Draw(img)

        try:
             # Fuente para texto (si está disponible)
             font = ImageFont.truetype("arial.ttf", 10) 
        except IOError:
             font = None
             print("Advertencia: No se encontró la fuente Arial para la imagen.")


        # 3. Dibujar la cuadrícula y el contenido de la cinta
        for paso_idx, cinta_str in enumerate(cintas):
            for celda_idx in range(max_len):
                
                x1 = margen + celda_idx * ancho_celda
                y1 = margen + paso_idx * alto_celda
                x2 = x1 + ancho_celda
                y2 = y1 + alto_celda
                
                simbolo = cinta_str[celda_idx] if celda_idx < len(cinta_str) else 'B'
                
                # Asignar color
                if simbolo == 'X':
                    fill_color = COLOR_X_AZUL
                elif simbolo == 'Y':
                    fill_color = COLOR_Y_VERDE
                elif simbolo == 'B':
                    fill_color = COLOR_BLANCO
                elif simbolo == '0':
                    fill_color = COLOR_0_GRIS
                elif simbolo == '1':
                    fill_color = COLOR_1_GRIS
                else: 
                    fill_color = (255, 165, 0)

                # Dibujar el rectángulo
                draw.rectangle([x1, y1, x2, y2], fill=fill_color, outline=(50, 50, 60))

                # Escribir el símbolo
                if font and simbolo != 'B':
                    text_fill = (0, 0, 0) if fill_color == COLOR_BLANCO else (255, 255, 255)
                    text_x = x1 + ancho_celda // 2
                    text_y = y1 + alto_celda // 2
                    draw.text((text_x, text_y), simbolo, font=font, fill=text_fill, anchor="mm")
                    
        # 4. Guardar la imagen
        img.save(nombre_archivo)
        print(f"\n*** Imagen del Proceso Guardada: {nombre_archivo} ***")
        
    except Exception as e:
        print(f"Ocurrió un error al generar la imagen: {str(e)}")


# --- EJECUCIÓN PRINCIPAL ---

if __name__ == "__main__":
    # Generar el archivo de log (simulación)
    maquina_turing()
    
    # Iniciar la visualización
    visualizar_turing()

    # Generar la imagen del proceso (si Pillow está disponible)
    generar_imagen_proceso()
