import logging
import os
import time
import argparse
from datetime import datetime
from cita_checker import AppointmentCheck
from utils import get_log_filename, get_stop_month

# Configurar logging


def main(email, password, locations, months, stop_month,blocked_days):
    logger = setup_logger(email)
    logger.info(f"Iniciando verificación de citas para {email}")
    try:
        checker = AppointmentCheck(email, password, locations, months, stop_month,blocked_days,logger)
        logger.info(f"RECIBIDO ARGS: {email} , {password},{locations},{months},{stop_month}")
        checker.check()
        logger.info(f"Verificación completada exitosamente para {email}")
    except Exception as e:
        logger.error(f"Error en la ejecución para {email}: {str(e)}")


def setup_logger(email: str) -> logging.Logger:
    """Configura un logger que escribe en un archivo específico dentro de la carpeta 'logs'."""
    log_folder = "logs"   # Aseguramos que la carpeta 'logs' exista 
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    log_filename = get_log_filename(email)
    logger = logging.getLogger(email)
    logger.setLevel(logging.INFO)
    # Evitar múltiples handlers en caso de reinicios
    if not logger.handlers:
        file_handler = logging.FileHandler(log_filename)
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', 
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ejecutar verificación de citas")
    parser.add_argument("--email", required=True, help="Correo del usuario")
    parser.add_argument("--password", required=True, help="Contraseña del usuario")
    parser.add_argument("--locations", required=True, help="Ubicaciones permitidas separadas por comas")
    parser.add_argument("--months", required=True, help="Meses permitidos separados por comas")
    parser.add_argument("--stop_month", required=True, help="Mes de detención")
    parser.add_argument("--blocked_days", required=True, help="Dias bloqueados")

    args = parser.parse_args()

    while True:
        main(
            email=args.email,
            password=args.password,
            locations=args.locations.split(","),
            months=args.months.split(","),
            stop_month=get_stop_month(args.stop_month),
            blocked_days=args.blocked_days.split(","),
        )
        time.sleep(60)  # Esperar 400 segundos antes del siguiente ciclo
