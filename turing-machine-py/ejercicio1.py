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
            pasos = [line.strip() for line in log_lines[1:] if line.strip()] #and not line.startswith("RECHAZO") and not line.startswith("Aceptación")]
    except FileNotFoundError:
        print(f"El archivo de log {archivo_salida} no se encontró.")
        return
    
    #Iniciamos la ventana principal de Tkinter
    ventana = tk.Tk()
    ventana.title("Máquina de Turing")

    #Componentes de la interfaz

    cinta_frame = ttk.Frame(root, relief = tk.RIDGE, borderwidth=2)
    cinta_frame.pack(padx = 10, pady = 20)

    

maquina_turing()

