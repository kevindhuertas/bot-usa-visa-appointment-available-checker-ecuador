import logging
import time
from datetime import datetime
from cita_checker import verificar_cita

# Configurar logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    logging.info("Iniciando verificación de citas")
    try:
        verificar_cita()
        logging.info("Verificación completada exitosamente")
    except Exception as e:
        logging.error(f"Error en la ejecución: {str(e)}")
    logging.info("Esperando próximo ciclo...")

if __name__ == "__main__":
    while True:
        main()
        # Esperar 30 minutos (1800 segundos)
        time.sleep(600)