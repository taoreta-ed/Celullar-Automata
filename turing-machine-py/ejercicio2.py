import tkinter as tk
from tkinter import ttk
import time

# --- CONFIGURACIÓN DE LA SIMULACIÓN ---

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

    estado = '0' # Estado inicial
    i = 0        # Posición del cabezal (índice)
    paso = 0     # Contador de pasos
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
                    # Movimiento a la izquierda: expandir cinta con 'B'
                    cinta.insert(0, 'B')
                    i = 0
                    simbolo_leido = cinta[i]
                
                elif i >= len(cinta):
                    # Movimiento a la derecha (fuera del límite): lee 'B'
                    simbolo_leido = 'B'
                    # No expandimos aquí; la expansión ocurre solo si la transición lo dicta (ej: escribir 'B')
                
                else:
                    # Cabezal dentro de los límites
                    simbolo_leido = cinta[i]

                # 2b. REGISTRO EN EL ARCHIVO LOG ANTES DE LA TRANSICIÓN
                cinta_str = "".join(cinta)
                log_file.write(f"{paso:02d} | {estado} | {i:02d} | {cinta_str}\n")
                
                # Impresión en consola para seguimiento
                print(f"Paso {paso:02d}: E{estado} lee '{simbolo_leido}' en pos. {i:02d}. Cinta: {cinta_str}")
                
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
                        resultado_final = "RECHAZO: Cadena no válida (E0)"
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
                        cinta[i] = 'Y' # CORRECCIÓN: Usar '=' para asignación
                        i += 1
                    else:
                        resultado_final = "RECHAZO: Cadena no válida (E1)"
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
                        resultado_final = "RECHAZO: Cadena no válida (E2)"
                        break

                # Estado 3
                elif estado == '3':
                    if simbolo_leido == 'Y':
                        nuevo_estado = '3'
                        cinta[i] = 'Y'
                        i += 1
                    elif simbolo_leido == 'B':
                        nuevo_estado = '4' # ACEPTACIÓN
                        resultado_final = "ACEPTACIÓN: Estado 4 alcanzado"
                        break
                    else:
                        resultado_final = "RECHAZO: Cadena no válida (E3)"
                        break

                # Caso de estado inesperado (Debería ser unreachable)
                else:
                    resultado_final = "RECHAZO: Error de estado interno"
                    break

                estado = nuevo_estado # Aplicamos la transición
            
            # 2d. REGISTRO FINAL FUERA DEL BUCLE
            if resultado_final.startswith("ACEPTACIÓN"):
                log_file.write(f"ACEPTACIÓN | Cinta final: {''.join(cinta)}\n")
            else:
                log_file.write(f"{resultado_final} | Cinta final: {''.join(cinta)}\n")
            
            print("-" * 30)
            print(f"*** SIMULACIÓN FINALIZADA: {resultado_final} ***")
            print(f"Cinta final: {''.join(cinta)}")
                
    except Exception as e:
        print(f"Ocurrió un error al escribir o durante la simulación: {str(e)}")


# --- CONFIGURACIÓN DE LA ANIMACIÓN GRÁFICA ---

def visualizar_turing(archivo_salida = "salida.txt"):
    """
    Lee el archivo de log y reproduce la simulación en una interfaz Tkinter.
    """
    try:
        # Leemos el archivo de log
        with open(archivo_salida, 'r') as archivo:
            log_lines = archivo.readlines()

        # Separamos los pasos de la cabecera y el resultado final
        log_steps = [line.strip() for line in log_lines[1:] if line.strip() and " | " in line]
        
    except FileNotFoundError:
        print(f"El archivo de log {archivo_salida} no se encontró. Ejecute la simulación primero.")
        return
    
    # Iniciamos la ventana principal de Tkinter
    root = tk.Tk()
    root.title("Máquina de Turing | Simulador 0ⁿ1ⁿ")
    root.configure(bg='#282c34') # Fondo oscuro

    # Estilo moderno
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TLabel', background='#282c34', foreground='#61dafb', font=('Consolas', 12))
    style.configure('TButton', font=('Consolas', 12, 'bold'), padding=10)

    # Componentes de la interfaz
    
    # Título
    ttk.Label(root, text="SIMULACIÓN MÁQUINA DE TURING", font=("Consolas", 18, "bold"), foreground='#FFFFFF').pack(pady=15)

    # Marco para la cinta
    cinta_frame = ttk.Frame(root, relief=tk.RAISED, borderwidth=4, style='TFrame')
    cinta_frame.pack(padx=10, pady=20)
    
    # Variables de estado
    estado_var = tk.StringVar(root, value="Estado: 0")
    ttk.Label(root, textvariable=estado_var, font=("Consolas", 14, "bold"), foreground='#a9f30b').pack(pady=5)

    paso_var = tk.StringVar(root, value="Paso: 00")
    ttk.Label(root, textvariable=paso_var, font=("Consolas", 12)).pack(pady=5)
    
    # Función de Dibujo de la Cinta (Labels)
    cinta_labels = []

    def draw_tape(cinta_str, cabezal_pos):
        # Limpiar frame anterior
        for widget in cinta_frame.winfo_children():
            widget.destroy()
        
        # Recorrer la cadena de la cinta y dibujar cada celda
        for index, symbol in enumerate(cinta_str):
            
            # Lógica de color DENTRO del bucle (CORRECCIÓN)
            bg_color = '#3c3f41' # Color de celda normal
            fg_color = '#FFFFFF'
            
            if index == cabezal_pos:
                bg_color = '#e06c75' # Color de celda del cabezal (rojo)
                fg_color = '#282c34' # Texto oscuro en cabezal
            
            # Crear y posicionar la etiqueta de la celda
            label = tk.Label( # Usar tk.Label para control directo de bg/fg
                cinta_frame,
                text=symbol,
                background=bg_color,
                foreground=fg_color,
                font=('Consolas', 18, 'bold'),
                width=3, # Ancho fijo para las celdas
                height=1,
                relief=tk.RIDGE
            )
            label.grid(row=0, column=index, padx=1, pady=1)

    # Función de Animación (Iterador)
    current_step = 0
    
    def next_step():
        nonlocal current_step

        if current_step < len(log_steps):
            line = log_steps[current_step]
            
            try:
                # Paso | Estado | Cabezal | Cinta (ej: 01 | 1 | 01 | X011)
                parts = line.split(" | ")
                paso_num = parts[0].strip()
                estado = parts[1].strip()
                cabezal = int(parts[2].strip())
                cinta_str = parts[3].strip()

                # Actualizar la interfaz
                paso_var.set(f"Paso: {paso_num}")
                
                # Intentamos leer el símbolo si el cabezal está en la cinta
                simbolo = cinta_str[cabezal] if cabezal < len(cinta_str) else 'B'
                estado_var.set(f"Estado: {estado} | Leyendo '{simbolo}' en Pos. {cabezal}")

                # Dibujar la cinta
                draw_tape(cinta_str, cabezal)

                current_step += 1

                # Llamarse a sí misma después de un tiempo (500ms)
                root.after(500, next_step) 

            except Exception as e:
                print(f"Error al procesar línea del log '{line}': {e}")
                current_step = len(log_steps) # Forzar el final si hay error de parsing

        else:
            # Fin de la animación
            estado_var.set("SIMULACIÓN FINALIZADA")
            final_status = log_lines[-1].strip()
            
            color = 'green' if final_status.startswith("ACEPTACIÓN") else 'red'
            
            ttk.Label(root, text=final_status, font=('Consolas', 16, 'bold'), foreground=color).pack(pady=10)
            start_button.config(text="Simulación Terminada", state=tk.DISABLED) # Desactivar botón

    # Botón para iniciar la animación
    start_button = ttk.Button(root, text="Iniciar Simulación", command=next_step)
    start_button.pack(pady=20)

    # Ejecutar la ventana de Tkinter
    root.mainloop()


if __name__ == "__main__":
    # Generar el archivo de log (simulación)
    maquina_turing()
    
    # Iniciar la visualización
    visualizar_turing()
