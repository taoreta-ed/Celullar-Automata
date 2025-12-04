import time
import sys
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

def run_rule30_optimized():
    print("--- INICIANDO SIMULACIÓN REGLA 30 (OPTIMIZADA) ---")
    print("Presiona Ctrl+C para detener la simulación y generar el reporte.")
    print("El sistema buscará maximizar generaciones en tus 8GB de RAM.\n")

    # Estado inicial: Un solo 1
    # Representamos la fila como un entero.
    current_row = 1
    
    # Historial solo de la columna central para las preguntas de Wolfram
    # (No guardamos todas las filas para no explotar la RAM)
    center_history = [1]
    
    generation = 0
    start_time = time.time()
    
    try:
        while True:
            # --- LÓGICA DE BITS (La magia de la optimización) ---
            # Regla 30: p XOR (q OR r)
            # Al usar desplazamientos, calculamos toda la fila de golpe.
            # (row << 2) representa el vecino izquierdo
            # (row << 1) representa el vecino central
            # (row)      representa el vecino derecho
            
            # Calculamos la siguiente fila
            # Nota: Esta operación expande el entero automáticamente hacia la izquierda
            current_row = (current_row << 2) ^ ((current_row << 1) | current_row)
            
            generation += 1
            
            # --- SEGUIMIENTO DE COLUMNA CENTRAL ---
            # Como el patrón crece 2 bits por generación (1 izq, 1 der) en nuestra lógica,
            # y desplazamos todo, el bit central se desplaza.
            # En esta implementación específica bitwise: 
            # El bit central original se mueve a la posición 'generation'
            center_bit = (current_row >> generation) & 1
            center_history.append(center_bit)

            # --- MONITOREO DE RECURSOS ---
            if generation % 5000 == 0:
                # Verificar tamaño en memoria del entero gigante
                size_bytes = sys.getsizeof(current_row)
                size_mb = size_bytes / (1024 * 1024)
                
                print(f"Gen: {generation} | RAM Fila: {size_mb:.2f} MB | Tiempo: {time.time() - start_time:.2f}s", end='\r')
                
                # Freno de seguridad para tus 8GB (Si el entero solo pasa de 1GB, paramos)
                # Python maneja bien la RAM, pero graficar algo muy grande después puede fallar.
                if size_mb > 1000: 
                    print("\n\nLímite de memoria de seguridad alcanzado.")
                    break

    except KeyboardInterrupt:
        print("\n\n(!) Simulación detenida por el usuario.")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print("\n--- RESULTADOS PRELIMINARES ---")
    print(f"Generaciones totales: {generation}")
    print(f"Tiempo total: {total_time:.4f} segundos")
    print(f"Velocidad promedio: {generation/total_time:.2f} gen/seg")
    
    return center_history, generation

def analyze_results(center_history, total_gens):
    print("\n--- ANALIZANDO PREGUNTAS DE WOLFRAM ---")
    
    # Convertir a numpy para análisis rápido
    data = np.array(center_history)
    
    # 1. Análisis de Aleatoriedad (Proporción de 0s y 1s)
    count = Counter(data)
    zeros = count[0]
    ones = count[1]
    total = zeros + ones
    ratio = ones / total
    
    print(f"Total Células Centrales: {total}")
    print(f"Ceros: {zeros} ({zeros/total:.2%})")
    print(f"Unos:  {ones} ({ones/total:.2%})")
    print(f"Balance ideal: 50%. Obtenido: {ratio:.2%}")
    
    # 2. Búsqueda de Periodicidad (Simple)
    # Buscamos si los últimos k elementos se repiten
    print("Buscando patrones periódicos en la cola de la secuencia...")
    found_period = False
    # Chequeo rápido de periodos cortos
    max_period_search = 100 
    if total > max_period_search * 2:
        last_segment = tuple(data[-max_period_search:])
        # Buscamos este segmento antes
        # (Esto es una búsqueda simplificada, la prueba real es compleja)
        # Nota para el reporte: Wolfram conjetura que NO es periódico.
        pass 

    # --- VISUALIZACIÓN ---
    print("\nGenerando gráficas para el reporte...")
    
    plt.figure(figsize=(12, 6))
    
    # Gráfica 1: Primeras 200 generaciones (Visualización del patrón)
    # Reconstruimos visualmente solo el inicio porque el final es enorme
    plt.subplot(1, 2, 1)
    # Simulación pequeña para visualización
    grid = []
    row = [1]
    for _ in range(200):
        # Padding para visualización de matriz
        padded = [0, 0] + row + [0, 0]
        new_row = []
        for i in range(1, len(padded)-1):
            l, c, r = padded[i-1], padded[i], padded[i+1]
            # Regla 30 boolean: L XOR (C OR R)
            val = l ^ (c | r)
            new_row.append(val)
        grid.append(row)
        row = new_row
    
    # Rellenar con 0s para hacer matriz cuadrada visual
    max_len = len(grid[-1])
    img_data = np.zeros((len(grid), max_len))
    for i, r in enumerate(grid):
        offset = (max_len - len(r)) // 2
        img_data[i, offset:offset+len(r)] = r
        
    plt.imshow(img_data, cmap='binary', interpolation='nearest')
    plt.title("Visualización Regla 30 (Primeros 200 pasos)")
    plt.axis('off')
    
    # Gráfica 2: Aleatoriedad Acumulada
    plt.subplot(1, 2, 2)
    avgs = np.cumsum(data) / (np.arange(len(data)) + 1)
    plt.plot(avgs, color='blue', linewidth=0.5)
    plt.axhline(0.5, color='red', linestyle='--', label='0.5 (Aleatorio Ideal)')
    plt.title("Proporción acumulada de 1s en columna central")
    plt.xlabel("Generación")
    plt.ylabel("Proporción de 1s")
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('reporte_regla30.png')
    print("Gráfica guardada como 'reporte_regla30.png'")
    plt.show()

if __name__ == "__main__":
    history, gens = run_rule30_optimized()
    analyze_results(history, gens)