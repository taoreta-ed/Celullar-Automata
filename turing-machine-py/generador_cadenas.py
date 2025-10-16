# generador_cadenas.py

import os

def generar_cadena_entrada(archivo_destino="entrada.txt"):
    """
    Genera una cadena del tipo 0^n 1^n y la guarda en el archivo de entrada.
    Permite al usuario elegir el valor de n y crear una cadena incorrecta.
    """
    
    print("--- GENERADOR DE CADENAS DE PRUEBA 0^n 1^n ---")
    
    # 1. Solicitar el número de dígitos (n)
    while True:
        try:
            n_input = input("¿De cuántos dígitos (n) debe ser la subcadena de 0's y 1's? (n >= 1): ")
            n = int(n_input)
            if n < 1:
                print("Por favor, introduce un número entero mayor o igual a 1.")
            else:
                break
        except ValueError:
            print("Entrada no válida. Por favor, introduce un número entero.")
            
    # 2. Construir la cadena CORRECTA (0^n 1^n)
    cadena_correcta = ('0' * n) + ('1' * n)
    cadena_a_guardar = cadena_correcta
    print(f"\nCadena correcta generada (0^{n}1^{n}): {cadena_correcta}")
    
    # 3. Opcionalmente, preguntar si quiere generar una cadena incorrecta
    modificar = input("¿Quieres modificar esta cadena para generar una INCORRECTA? (s/N): ").strip().lower()
    
    if modificar == 's':
        # Ejemplo simple de cadena incorrecta: cambiar el último '1' por '0'
        if len(cadena_correcta) >= 1:
            cadena_incorrecta = list(cadena_correcta)
            # Intentar cambiar el último carácter. Si hay '1's, se cambia el último '1'.
            try:
                # Buscar la posición del último '1' (si n >= 1)
                pos_ultimo_uno = len(cadena_incorrecta) - 1
                if cadena_incorrecta[pos_ultimo_uno] == '1':
                    cadena_incorrecta[pos_ultimo_uno] = '0'
                    cadena_a_guardar = "".join(cadena_incorrecta)
                    print(f"Cadena INCORRECTA generada (cambio simple): {cadena_a_guardar}")
                else:
                    # En caso de que n=0 (aunque se previene con el n>=1), o la lógica fuera otra
                    cadena_a_guardar = cadena_correcta # Usar la correcta si no se pudo modificar
                    print("No se pudo aplicar la modificación simple. Usando la cadena correcta.")
            except IndexError:
                # Esto no debería pasar con n >= 1
                cadena_a_guardar = cadena_correcta
                print("Error al intentar modificar. Usando la cadena correcta.")
        else:
            cadena_a_guardar = cadena_correcta
            print("La cadena está vacía. Usando la cadena correcta.")
    
    # 4. Guardar la cadena en el archivo de entrada
    try:
        with open(archivo_destino, 'w') as archivo:
            archivo.write(cadena_a_guardar)
        print(f"\n*** Cadena '{cadena_a_guardar}' guardada exitosamente en {archivo_destino} ***")
    except Exception as e:
        print(f"Error al escribir en el archivo {archivo_destino}: {e}")

if __name__ == "__main__":
    generar_cadena_entrada()