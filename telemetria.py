# telemetria.py
import csv
import os

NOMBRE_ARCHIVO = "test/log_telemetria_drift.csv"


def registrar_drift(estado, valor_fisico, velocidad, cambio, dt):
    """
    Guarda los datos técnicos en un archivo CSV para análisis posterior.
    """
    # Si la carpeta test no existe, la creamos
    carpeta = 'test'
    os.makedirs(carpeta, exist_ok=True)

    # Si el archivo no existe, lo creamos con encabezados
    es_nuevo = not os.path.exists(NOMBRE_ARCHIVO)

    try:
        with open(NOMBRE_ARCHIVO, mode='a', newline='') as f:
            writer = csv.writer(f)
            if es_nuevo:
                writer.writerow(['Tiempo_Unix', 'RY_Fisico',
                                'RX', 'Velocidad', 'Cambio', 'DeltaTime'])

            # Guardamos los datos
            import time
            writer.writerow([
                time.time(),
                round(valor_fisico, 6),
                round(estado['RX'], 6),
                round(velocidad, 6),
                round(cambio, 6),
                round(dt, 6)
            ])
    except Exception as e:
        print(f"Error guardando telemetría: {e}")

# Opcional: una función para avisar que estamos grabando


def mensaje_grabando():
    print(">>> GRABANDO TELEMETRÍA EN CSV...")
