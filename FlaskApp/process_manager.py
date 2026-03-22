import subprocess
import os
import signal

# Función para iniciar el proceso; se invoca el script main.py con los parámetros necesarios
def start_process(config):
    args = [
        "python3", "./main.py",
        "--email", config["USER_EMAIL"],
        "--password", config["USER_PASSWORD"],
        "--locations", ",".join(config["allowed_location_to_save_appointment"]),
        "--months", ",".join(config["allowed_months_to_save_appointment"]),
        "--blocked_days", ",".join(config["blocked_days"]),
        "--stop_month", config["stop_month"],
        "--user_id", config["user_id"],
        "--appoinment_id", config["appoinment_id"],
        "--country", config.get("country", "Ecuador")
    ]
    # Iniciar el proceso en background
    process = subprocess.Popen(args)
    return process.pid

def stop_process(process_id):
    from models import get_process_by_id, update_process
    proc = get_process_by_id(process_id)
    print(f"Intentando detener proceso con ID: {process_id}, encontrado proceso: {proc}")
    
    if not proc:
        return None, "El proceso no existe"
        
    if proc.get('status') != 'active':
        return proc, "El proceso ya se encuentra inactivo"
        
    pid = proc.get('pid')
    error_msg = None
    
    try:
        if pid:
            if isinstance(pid, str) and pid.isdigit():
                pid = int(pid)
            print(f"DETENIENDO PROCESO: de id {process_id} con id {pid}")
            os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        error_msg = "Error con el proceso en el sistema (no existe o ya terminó)"
        print(error_msg)
    except Exception as e:
        error_msg = f"Error al detener el proceso en el sistema: {str(e)}"
        print(error_msg)
        
    # En cualquier caso (ya sea que os.kill falle o no), marcamos como inactivo si estaba activo
    proc['status'] = 'inactive'
    proc['pid'] = ''
    updated_proc, error = update_process(process_id, proc)
    
    if error:
        return None, f"Error actualizando la base de datos: {error}"
        
    return updated_proc, error_msg

def get_process_status(pid):
    if not pid:
        return False
    try:
        if isinstance(pid, str) and pid.isdigit():
            pid = int(pid)
        # Intenta enviar una señal 0 para comprobar si el proceso existe
        os.kill(pid, 0)
        return True
    except:
        return False
