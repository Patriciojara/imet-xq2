import subprocess
import time

while True:
    # Ejecuta el archivo "cortador.py"
    resultado = subprocess.run(["python", "cortador.py"], capture_output=True, text=True)

    # Muestra la salida del script
    print(resultado.stdout)
    time.sleep(2)  # Espera 5 segundos antes de ejecutar nuevamente
