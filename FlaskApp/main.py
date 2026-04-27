import logging
import os
from random import random
import time
import argparse
from datetime import datetime
from cita_checker import AppointmentCheck
from cita_checker_colombia import AppointmentCheckColombia
from utils import get_log_filename, get_stop_month

def main(email, 
         password, 
         locations, 
         months,
        stop_month,
        blocked_days,
        user_id,
        appoinment_id,
        country,
        user_email_alert,
        auto_programacion_allowed,
        nearest_cas_appointment,
        # allowed_sas_days=None, 
        current_consular_appointment_date=None
        ):
    logger = setup_logger(email)
    logger.info(f"Iniciando verificación de citas para {email} en {locations} para los meses {months} para la cita_id de {appoinment_id} en {country} ")
    logger.info(f"CLIENT: Iniciado busqueda de la cita mas cercana para {email} con autoprogramación {'activada' if auto_programacion_allowed else 'desactivada'}")
    try:
        if(country.lower() == "colombia"):
            checker = AppointmentCheckColombia(
                email, password, locations, months, stop_month, blocked_days, 
                logger, user_id, appoinment_id, country, user_email_alert, 
                auto_programacion_allowed, nearest_cas_appointment, current_consular_appointment_date
            )
        else:
            checker = AppointmentCheck(email, password, locations, months, stop_month,blocked_days,logger,user_id, appoinment_id, country,user_email_alert,auto_programacion_allowed)
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
    parser.add_argument("--country", required=True, help="Country del usuario")
    parser.add_argument("--user_email_alert", required=True, help="Email de alerta del usuario")
    parser.add_argument("--auto_programacion_allowed", required=True, help="Permitir autoprogramación")

    # Nuevas variables (Opcionales globalmente, pero debes enviarlas si es Colombia)
    parser.add_argument("--nearest_cas_appointment", required=False, default='true', help="Orden de cita CAS más cercana encontrada (Requerido para Colombia)")
    parser.add_argument("--current_consular_appointment_date", required=False, default=None, help="Fecha actual de la cita consular (Requerido para Colombia)")

    args = parser.parse_args()

    cycle_interval_min = 70
    cycle_interval_max = 100
    
    import random
    while True:
        is_auto_allowed = args.auto_programacion_allowed.lower() == 'true'
        # sas_days_list = args.allowed_sas_days.split(",") if args.allowed_sas_days else []
        nearest_cas_appointment = args.nearest_cas_appointment.lower() == 'true'
        main(
            email=args.email,
            password=args.password,
            locations=args.locations.split(","),
            months=args.months.split(","),
            stop_month=get_stop_month(args.stop_month),
            blocked_days=args.blocked_days.split(","),
            user_id=args.user_id,
            appoinment_id=args.appoinment_id,
            country=args.country,
            user_email_alert=args.user_email_alert,
            auto_programacion_allowed=is_auto_allowed,
            
            #COLOMBIA
            nearest_cas_appointment=nearest_cas_appointment,                                    
            current_consular_appointment_date=args.current_consular_appointment_date 
        )
        sleep_time = random.randint(cycle_interval_min, cycle_interval_max)
        time.sleep(sleep_time)
