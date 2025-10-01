#from os import *
#from sys import *
#import sys
#from collections import deque #para cintas más grandes

def maquina_turing(archivo_entrada = "entrada.txt"):
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

    while estado != '4':
        print("cinta: ", cinta)
        
        #Para el estado 0
        if estado == '0':
            print("Estado 0: ")
            if cinta[i] == '0':
                estado = '1'
                cinta[i] = 'X'
                i+=1
            elif cinta[i] == 'Y':
                estado = '3'
                cinta[i] = 'Y'
                i+=1
            else:
                print("Cadena no válida")
                break
        
        #Para el estado 1
        elif estado == '1':
            print("Estado 1: ")
            if cinta[i] == '0':
                estado = '1'
                cinta[i] = '0'
                i+=1
            elif cinta[i] == '1':
                estado = '2'
                cinta[i] = 'Y'
                i-=1
            elif cinta[i] == 'Y':
                estado = '1'
                cinta[i] == 'Y'
                i+=1
            else:
                print("Cadena no válida")
                break

        #Para el estado 2
        elif estado == '2':
            print("Estado 2: ")
            if cinta[i] == '0':
                estado = '2'
                cinta[i] = '0'
                i-=1
            elif cinta[i] == 'X':
                estado = '0'
                cinta[i] = 'X'
                i+=1
            elif cinta[i] == 'Y':
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
            elif cinta[i] == 'Y':
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


maquina_turing()