import logging
import os
import time
import argparse
from datetime import datetime
from cita_checker import AppointmentCheck
from utils import get_log_filename, get_stop_month

# Configurar logging
def main(email, password, locations, months, stop_month,blocked_days,user_id, appoinment_id):
    logger = setup_logger(email)
    logger.info(f"Iniciando verificación de citas para {email} en {locations} para los meses {months} para la cita_id de {appoinment_id}")
    try:
        checker = AppointmentCheck(email, password, locations, months, stop_month,blocked_days,logger,user_id, appoinment_id)
        checker.check()
        logger.info(f"Check completado exitosamente para {email}")
    except Exception as e:
        logger.error(f"Error en la ejecución para {email}: {str(e)}")


def setup_logger(email: str) -> logging.Logger:
    log_folder = "logs" 
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
    parser.add_argument("--user_id", required=True, help="User id del usuario")
    parser.add_argument("--appoinment_id", required=True, help="Appointment id del usuario")

    args = parser.parse_args()

    while True:
        main(
            email=args.email,
            password=args.password,
            locations=args.locations.split(","),
            months=args.months.split(","),
            stop_month=get_stop_month(args.stop_month),
            blocked_days=args.blocked_days.split(","),
            user_id=args.user_id,
            appoinment_id=args.appoinment_id,
        )

        time.sleep(45)  # Esperar 400 segundos antes del siguiente ciclo
