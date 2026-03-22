import json
import os
from datetime import datetime

from main import get_log_filename
from supabase_client import create_record, read_records, update_record, delete_record

# JSON_FILE = 'processes.json' # deprecated, using supabase now

def map_process_to_db(proc):
    return {
        "process_id": proc.get("process_id"),
        "appointment_id": proc.get("appoinment_id"), # based on start_process args
        "user_id": proc.get("user_id"),
        "user_email": proc.get("USER_EMAIL"),
        "allowed_locations": proc.get("allowed_location_to_save_appointment", []),
        "allowed_months": proc.get("allowed_months_to_save_appointment", []),
        "stop_month": proc.get("stop_month"),
        "blocked_days": proc.get("blocked_days", []),
        "status": proc.get("status", "inactive"),
        "pid": str(proc.get("pid", "")),
        "process_finished": proc.get("process_finished", False),
    }

def map_db_to_process(db_proc):
    return {
        "process_id": db_proc.get("process_id"),
        "appoinment_id": db_proc.get("appointment_id"),
        "user_id": db_proc.get("user_id"),
        "USER_EMAIL": db_proc.get("user_email"),
        "allowed_location_to_save_appointment": db_proc.get("allowed_locations", []),
        "allowed_months_to_save_appointment": db_proc.get("allowed_months", []),
        "stop_month": db_proc.get("stop_month"),
        "blocked_days": db_proc.get("blocked_days", []),
        "status": db_proc.get("status", "inactive"),
        "pid": db_proc.get("pid", ""),
        "process_finished": db_proc.get("process_finished", False),
    }

def load_processes():
    try:
        response = read_records("processes")
        if response.data:
            return [map_db_to_process(p) for p in response.data]
        return []
    except Exception as e:
        print(f"Error loading processes: {e}")
        return []

def save_processes(processes):
    pass # Managed individually via add/update/delete now

def add_process(new_proc):
    try:
        db_data = map_process_to_db(new_proc)
        print(db_data)
        db_data["process_create_date"] = datetime.now().isoformat()
        create_record("processes", db_data)
        return True, None
    except Exception as e:
        print(f"Error adding process: {e}")
        return False, str(e)

def list_processes():
    return load_processes()

def get_process_by_email(user_email):
    try:
        response = read_records("processes", {"user_email": user_email})
        if response.data and len(response.data) > 0:
            return map_db_to_process(response.data[0])
        return None
    except Exception as e:
        print(f"Error getting process by email: {e}")
        return None

def get_process_by_email_and_user(user_email, user_id):
    try:
        response = read_records("processes", {"user_email": user_email, "user_id": user_id})
        if response.data and len(response.data) > 0:
            return map_db_to_process(response.data[0])
        return None
    except Exception as e:
        print(f"Error getting process by email and user: {e}")
        return None

def get_process_by_id(process_id):
    try:
        response = read_records("processes", {"process_id": process_id})
        if response.data and len(response.data) > 0:
            return map_db_to_process(response.data[0])
        return None
    except Exception as e:
        print(f"Error getting process by id: {e}")
        return None

def update_process(process_id, updated_proc):
    try:
        proc = get_process_by_id(process_id)
        if not proc:
            return None, "Proceso no encontrado"
        print(f"Proceso {proc}, UPDATE with: {updated_proc}")
        # Permitir edición solo si el proceso está inactivo
        if proc.get('status') == 'active' and updated_proc.get('status') == 'active':
            return None, "No se puede editar un proceso activo"
        
        db_data = map_process_to_db(updated_proc)
        update_record("processes", "process_id", process_id, db_data)
        return updated_proc, None
    except Exception as e:
        print(f"Error updating process: {e}")
        return None, str(e)

def delete_process(process_id):
    try:
        proc = get_process_by_id(process_id)
        if not proc:
            return False, "Proceso no encontrado"
        
        # Solo eliminar si está inactivo
        if proc.get('status') == 'inactive':
            delete_record("processes", "process_id", process_id)
            return True, None
        else:
            return False, "El proceso debe estar inactivo para poder eliminarlo"
    except Exception as e:
        print(f"Error deleting process: {e}")
        return False, str(e)

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

def update_process_checks(user_email):
    # This might require a check_count field in processes or users.
    # The current supabase schema for processes doesn't have check_count.
    # Assuming we want to update it in memory or it's handled differently.
    try:
        proc = get_process_by_email(user_email)
        if proc:
            # We don't have check_count in the provided schema for processes, 
            # maybe it's in users table?
            # Let's just return the process for now, or update if we add it.
            pass
        return proc
    except Exception as e:
        print(f"Error updating process checks: {e}")
        return None

def update_process_error(user_email, error_message):
    try:
        proc = get_process_by_email(user_email)
        if proc:
            if error_message is not None:
                proc['status'] = "inactive"
                db_data = map_process_to_db(proc)
                update_record("processes", "user_email", user_email, db_data)
            return proc
    except Exception as e:
        print(f"Error updating process error: {e}")
        return None