import subprocess
import time

while True:
    # Ejecuta el archivo "cortador.py"
    resultado = subprocess.run(["python", "cortador.py"], capture_output=True, text=True)

    envia = subprocess.run(["python", "envia_entrada.py", resultado], capture_output=True, text=True)
    
    # Muestra la salida del script
    print(resultado.stdout)
    print(envia.stdout)
    time.sleep(0.1)  # Espera 5 segundos antes de ejecutar nuevamente
