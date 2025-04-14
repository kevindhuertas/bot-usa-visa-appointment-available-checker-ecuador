import json
import os

from main import get_log_filename

JSON_FILE = 'processes.json'

def load_processes():
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, 'r') as f:
        return json.load(f)

def save_processes(processes):
    print(f"SAVE PROCESS: {processes}")
    with open(JSON_FILE, 'w') as f:
        json.dump(processes, f, indent=4)

def add_process(new_proc):
    processes = load_processes()
    processes.append(new_proc)
    save_processes(processes)

def list_processes():
    return load_processes()

def get_process_by_email(user_email):
    processes = load_processes()
    for proc in processes:
        if proc.get('USER_EMAIL') == user_email:
            return proc
    return None

def update_process(user_email, updated_proc):
    processes = load_processes()
    updated = False
    for idx, proc in enumerate(processes):
        if proc.get('USER_EMAIL') == user_email:
            print(f"Proceso {proc}, UPDATE with: {updated_proc}")
            # Permitir edición solo si el proceso está inactivo
            if proc.get('status') == 'active' and updated_proc.get('status') == 'active':
                return None
            processes[idx] = updated_proc
            updated = True
            break
    if updated:
        save_processes(processes)
        return updated_proc
    return None

def delete_process(user_email):
    processes = load_processes()
    new_processes = []
    deleted = False
    for proc in processes:
        if proc.get('USER_EMAIL') == user_email:
            # Solo eliminar si está inactivo
            if proc.get('status') == 'inactive':
                deleted = True
                continue
            else:
                return None
        new_processes.append(proc)
    if deleted:
        save_processes(new_processes)
        # delete_log_file(user_email)
        return True
    return False


def delete_log_file(email: str) -> bool:
    log_file = get_log_filename(email)
    try:
        if os.path.exists(log_file):
            os.remove(log_file)
            return True
        else:
            return True  # No existe, se considera eliminado
    except Exception as e:
        print(f"ERROR eliminando el LOG para {email}: {str(e)}")
        return False

