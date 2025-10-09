#from os import *
#from sys import *
#import sys
#from collections import deque #para cintas más grandes

#importaciones para la animación
import tkinter as tk
from tkinter import ttk
import time


def maquina_turing(archivo_entrada = "entrada.txt", archivo_salida = "salida.txt"):
    #cinta = "0011" #list() #La cadena a leer
    #cinta = ['0', '0', '1', '1']
    
    #La cinta la obtenemos de un archivo
    try:
        with open(archivo_entrada, 'r') as archivo:
            #Lee la primer línea y quita espacios y saltos de linea
            cadena_entrada = archivo.readline().strip()

            #Convierte la cadena en un arreglo de chars
            cinta = list(cadena_entrada)
    except FileNotFoundError:
        print(f"Error: El archivo de entrada {archivo_entrada} no se encontró")
        return

    estado = '0' #Los estados pueden ser 0, 1, 2 y 3

    #Vamos a tener diferentes condiciones dependiendo del estado y el simbolo a leer

    i = 0 #iterador que nos ayuda a saber en que posición de la cinta estamos
    paso = 0 #iterador que cuenta en qué paso vamos

    try:
        #Vamos a abrir el archivo donde guardaremos los datos
        with open(archivo_salida, 'w') as salida:
            salida.write("Paso | Estado | Cabezal | Cinta\n")

        
            while estado != '4':
                print("cinta: ", cinta)
                paso +=1
                
                
                #Revisar que el iterador esté dentro de los límites
                simbolo_leido = "" #Esta variable la usamos para comparaciones, no para asignar
                if i < 0:
                    #Movimiento a la izquierda, inserta un espacio en blanco ("B") y vuelve al índice 0
                    cinta.insert(0, 'B')
                    i = 0
                    simbolo_leido = cinta[i]
                elif i >= len(cinta):
                    #Movimiento a la derecha fuera del límite, hay un Blanco
                    #Falta agregar la lógica para manejar 'B' Si es necesario
                    simbolo_leido = 'B'
                else:
                    #Todo bien (cabezal dentro de los límites)
                    simbolo_leido = cinta[i]

                #Log al archivo
                salida.write(f"{paso:02d} | {estado} | {i:02d} | {"".join(cinta)}\n")

                #Para el estado 0
                if estado == '0':
                    print("Estado 0: ")
                    if simbolo_leido == '0':
                        estado = '1'
                        cinta[i] = 'X'
                        i+=1
                    elif simbolo_leido == 'Y':
                        estado = '3'
                        cinta[i] = 'Y'
                        i+=1
                    else:
                        print("Cadena no válida")
                        break
                
                #Para el estado 1
                elif estado == '1':
                    print("Estado 1: ")
                    if simbolo_leido == '0':
                        estado = '1'
                        cinta[i] = '0'
                        i+=1
                    elif simbolo_leido == '1':
                        estado = '2'
                        cinta[i] = 'Y'
                        i-=1
                    elif simbolo_leido == 'Y':
                        estado = '1'
                        cinta[i] == 'Y'
                        i+=1
                    else:
                        print("Cadena no válida")
                        break

                #Para el estado 2
                elif estado == '2':
                    print("Estado 2: ")
                    if simbolo_leido == '0':
                        estado = '2'
                        cinta[i] = '0'
                        i-=1
                    elif simbolo_leido == 'X':
                        estado = '0'
                        cinta[i] = 'X'
                        i+=1
                    elif simbolo_leido == 'Y':
                        estado = '2'
                        cinta[i] = 'Y'
                        i-=1
                    else:
                        print("Cadena no válida")
                        break

                #Para el estado 3
                elif estado == '3':
                    print("Estado 3: ")
                    if i == len(cinta):
                        estado = '4'
                        print(cinta)
                        print("Estado 4: Estado de aceptación")
                    elif simbolo_leido == 'Y':
                        estado = '3'
                        cinta[i] = 'Y'
                        i+=1
                    else:
                        print("Cadena no válida")
                        break

                #Para el estado 4
                else:
                    print("Cadena no válida")
                    break
    except Exception as e:
        print("Ocurró un error al escribir o durante la simulación: " + e)


#Función para la animación
def visualizar_turing(archivo_salida = "salida.txt"):
    try:
        #Leemos el archivo de log
        with open(archivo_salida, 'r') as archivo:
            log_lines = archivo.readlines()

            #Ignoramos el encabezado
            log_steps = [line.strip() for line in log_lines[1:] if line.strip()] #and not line.startswith("RECHAZO") and not line.startswith("Aceptación")]
    except FileNotFoundError:
        print(f"El archivo de log {archivo_salida} no se encontró.")
        return
    
    #Iniciamos la ventana principal de Tkinter
    root = tk.Tk()
    root.title("Máquina de Turing")

    #Componentes de la interfaz
    ##Marco o frame para la cinta
    cinta_frame = ttk.Frame(root, relief = tk.RIDGE, borderwidth=2)
    cinta_frame.pack(padx = 10, pady = 20)

    #Etiqueta para el estado actual
    estado_var = tk.StringVar(root, value="Estado: 0")
    ttk.Label(root, textvariable=estado_var, font=("Consolas", 14, "bold")).pack(pady=5)

    #Etiqueta para el paso actual
    paso_var = tk.StringVar(root, value="Paso: 00")
    ttk.Label(root, textvariable=paso_var, font=("Consolas", 12)).pack(pady=5)
    
    #Función de Dibujo de la Cinta (Canvas o Labels)

    #Usaremos una lista de etiquetas para representar las celdas de la cinta
    cinta_labels = []

    def draw_tape(cinta_str, cabezal_pos):
        nonlocal cinta_labels

        #Limpiar frame anterior
        for widget in cinta_frame.winfo_children():
            widget.destroy()
        cinta_labels = []

        #Recorrer la cadena de la cinta y dibujar la celda
        for index, symbol in enumerate(cinta_str):
            bg_color = 'red' #Color para el cabezal
            fg_color = 'white' 

        #Crear y posicionar la etiqueta de la celda
        label = ttk.Label(
            cinta_frame,
            text=symbol,
            background=bg_color,
            foreground=fg_color,
            font=('Consolas', 16, 'bold'),
            padding=(10, 5)
        )
        label.grid(row=0, column=index, padx=1, pady=1)
        cinta_labels.append(label)

    #Funcion de Animación (Iterador)

    current_step = 0

    def next_step():
        nonlocal current_step

        if current_step < len(log_steps):
            line = log_steps[current_step]
            # Paso | Estado | Cabezal | Cinta (ej: 01 | 1 | 01 | X011)
            try:
                #Parsear la línea del log
                parts = line.split(" | ")
                paso_num = parts[0].strip()
                estado = parts[1].strip()
                cabezal = int(parts[2].strip())
                cinta_str = parts[3].strip()

                #Actualizar las variables de la interfaz
                paso_var.set(f"Paso: {paso_num}")
                estado_var.set(f"Estado: {estado} (Leyendo '{cinta_str[cabezal]}' en pos. {cabezal})")

                #Dibujar la cinta
                draw_tape(cinta_str, cabezal)

                current_step += 1

                #Llamarse a sí misma después de un tiempo (500ms)
                root.after(500, next_step) #500 milisegundos

            except Exception as e:
                print(f"Error al procesar línea del log '{line}': {e}")

        else:
            #Fin de la animación
            estado_var.set("SIMULACIÓN FINALIZADA")
            final_status = log_lines[-1].strip() #Obtener el resultado final del log
            ttk.Label(root, text=final_status, font=('Consolas', 16, 'bold'), foreground='green').pack(pady=10)

    #Botón para iniciar la animación
    star_button = ttk.Button(root, text="Iniciar Simulación", command=next_step)
    star_button.pack(pady=20)

    #Ejecutar la ventana de Tkinter
    root.mainloop()


    

maquina_turing()
visualizar_turing()