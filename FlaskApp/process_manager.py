import subprocess
import os
import signal

# Función para iniciar el proceso; se invoca el script main.py con los parámetros necesarios
def start_process(config):
    # Armamos la lista de argumentos, por ejemplo:
    args = [
        "python3", "./main.py",
        "--email", config["USER_EMAIL"],
        "--password", config["USER_PASSWORD"],
        "--locations", ",".join(config["allowed_location_to_save_appointment"]),
        "--months", ",".join(config["allowed_months_to_save_appointment"]),
        "--blocked_days", ",".join(config["blocked_days"]),
        "--stop_month", config["stop_month"],
        "--user_id", config["user_id"],
        "--appoinment_id", config["appoinment_id"]
    ]
    # Iniciar el proceso en background
    process = subprocess.Popen(args)
    return process.pid

def stop_process(user_email):
    from models import get_process_by_email, update_process
    proc = get_process_by_email(user_email)
    if not proc or proc.get('status') != 'active':
        return None
    pid = proc.get('pid')
    try:
        print(f"DETENIENDO PROCESO: de{user_email} con id {pid}")
        os.kill(pid, signal.SIGTERM)
        proc['status'] = 'inactive'
        proc['pid'] = ''
        update_process(user_email, proc)
        return proc
    except Exception as e:
        print(f"Error al detener el proceso: {e}")
        return None

def get_process_status(pid):
    try:
        # Intenta enviar una señal 0 para comprobar si el proceso existe
        os.kill(pid, 0)
        return True
    except:
        return False
