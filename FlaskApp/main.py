import logging
import time
import argparse
from datetime import datetime
from FlaskApp.cita_checker import AppointmentCheck
from utils import get_stop_month

# Configurar logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def main(email, password, locations, months, stop_month,blocked_days):
    logging.info(f"Iniciando verificación de citas para {email}")
    try:
        logging.info(f"RECIBIDO ARGS: {email} , {password},{locations},{months},{stop_month}")
        checker = AppointmentCheck(email, password, locations, months, stop_month,blocked_days)
        checker.check()
        logging.info(f"Verificación completada exitosamente para {email}")
    except Exception as e:
        logging.error(f"Error en la ejecución para {email}: {str(e)}")

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
