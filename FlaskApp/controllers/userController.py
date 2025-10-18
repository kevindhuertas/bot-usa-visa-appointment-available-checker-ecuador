import json
import os
import uuid # Para generar IDs únicos si es necesario

USERS_JSON_FILE = './users.json'

# --- Funciones base para cargar y guardar ---
def load_users():
    """Carga los usuarios desde el archivo JSON."""
    if not os.path.exists(USERS_JSON_FILE):
        return []
    try:
        with open(USERS_JSON_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
            # Asegurarse de que siempre devolvemos una lista
            return users if isinstance(users, list) else []
    except json.JSONDecodeError:
        print(f"Advertencia: El archivo {USERS_JSON_FILE} contiene JSON inválido o está vacío. Se tratará como una lista vacía.")
        return []
    except Exception as e:
        print(f"Error cargando usuarios: {e}")
        return []

def save_users(users):
    """Guarda la lista de usuarios en el archivo JSON."""
    try:
        with open(USERS_JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando usuarios: {e}")

# --- CRUD Básico ---
def get_all_users():
    """Obtiene todos los usuarios."""
    return load_users()

def get_user_by_id(user_id: str):
    """Obtiene un usuario por su ID."""
    users = load_users()
    for user in users:
        if user.get('id') == user_id:
            return user
    return None

def create_user(new_user_data: dict):
    """Crea un nuevo usuario.
    Asegúrate de que new_user_data tenga un 'id' único o géneralo aquí.
    """
    users = load_users()
    if 'id' not in new_user_data:
        new_user_data['id'] = str(uuid.uuid4()) # Genera un ID único si no se provee
        print(f"Nuevo usuario no tenía ID, se generó: {new_user_data['id']}")

    # Verificar si el ID ya existe
    if any(u.get('id') == new_user_data['id'] for u in users):
        print(f"Error: El usuario con ID {new_user_data['id']} ya existe.")
        return None
    
    # Valores por defecto si no se proveen para los campos importantes
    new_user_data.setdefault('checksCount', "0")
    new_user_data.setdefault('processfinished', "0") # Asumo que es un contador también
    new_user_data.setdefault('processFinishedHistory', [])
    if 'plan' not in new_user_data:
        new_user_data['plan'] = {
            "type": "processCount",
            "processProgramationAvalaible": "0", # Default
            "processChekingAvalaible": "0", # Default
            "planExpiration": "",
            "planRenewed": "",
            "planStarted": ""
        }
    else:
        new_user_data['plan'].setdefault("processProgramationAvalaible", "0")
        new_user_data['plan'].setdefault("processChekingAvalaible", "0")


    users.append(new_user_data)
    save_users(users)
    print(f"Usuario '{new_user_data.get('username')}' creado con ID: {new_user_data['id']}.")
    return new_user_data

def update_user_full(user_id: str, updated_user_data: dict):
    """Actualiza toda la información de un usuario existente por su ID.
    'updated_user_data' debe contener todos los campos del usuario.
    El ID en updated_user_data debe coincidir con user_id.
    """
    users = load_users()
    user_found = False
    for i, user in enumerate(users):
        if user.get('id') == user_id:
            # Asegurarse de que el ID no se cambie accidentalmente si está en updated_user_data
            if 'id' in updated_user_data and updated_user_data['id'] != user_id:
                print(f"Error: No se puede cambiar el ID del usuario durante la actualización.")
                return None
            
            updated_user_data_copy = updated_user_data.copy()
            updated_user_data_copy['id'] = user_id # Asegurar que el ID original se mantiene

            users[i] = updated_user_data_copy
            user_found = True
            break
    
    if user_found:
        save_users(users)
        print(f"Usuario con ID '{user_id}' actualizado completamente.")
        return users[i] # Retorna el usuario actualizado
    else:
        print(f"Error: Usuario con ID '{user_id}' no encontrado para actualizar.")
        return None

def delete_user(user_id: str):
    """Elimina un usuario por su ID."""
    users = load_users()
    original_length = len(users)
    users = [user for user in users if user.get('id') != user_id]
    
    if len(users) < original_length:
        save_users(users)
        print(f"Usuario con ID '{user_id}' eliminado.")
        return True
    else:
        print(f"Error: Usuario con ID '{user_id}' no encontrado para eliminar.")
        return False

# --- Funciones Específicas ---
def update_user_field(user_id: str, field: str, value):
    """Actualiza un campo específico de un usuario.
    Soporta campos anidados usando punto como separador (ej: "plan.type").
    """
    users = load_users()
    user_to_update = None
    user_index = -1

    for i, u in enumerate(users):
        if u.get('id') == user_id:
            user_to_update = u
            user_index = i
            break

    if not user_to_update:
        print(f"Error: Usuario con ID '{user_id}' no encontrado para actualizar campo.")
        return None

    # Manejo de campos anidados
    keys = field.split('.')
    current_level = user_to_update
    
    for k_idx, key_part in enumerate(keys[:-1]): # Navegar hasta el penúltimo nivel
        if isinstance(current_level, dict) and key_part in current_level:
            current_level = current_level[key_part]
        else:
            print(f"Error: Campo anidado '{field}' no encontrado o estructura incorrecta en usuario ID '{user_id}'.")
            return None # Ruta no válida

    last_key = keys[-1]
    if isinstance(current_level, dict) and last_key in current_level:
        current_level[last_key] = value
    elif isinstance(current_level, dict) and not last_key in current_level: # Si el campo no existe, lo crea
         current_level[last_key] = value
    else: # Si es un campo de primer nivel
        user_to_update[field] = value
        # print(f"Error: No se pudo establecer el campo '{last_key}' en el nivel '{'.'.join(keys[:-1]) if keys[:-1] else 'raíz'}'.")
        # return None


    users[user_index] = user_to_update # Actualizar la lista principal
    save_users(users)
    print(f"Usuario ID '{user_id}', campo '{field}' actualizado a '{value}'.")
    return user_to_update

def add_checks_count(user_id: str):
    """Suma 1 al 'checksCount' de un usuario.
    ADVERTENCIA: Esta operación de lectura/escritura frecuente en JSON es ineficiente y
    propensa a errores de concurrencia sin un mecanismo de bloqueo.
    """
    # --- INICIO DE SECCIÓN CRÍTICA (si hubiera múltiples procesos/hilos) ---
    # Aquí iría la lógica de bloqueo de archivo si se implementa
    users = load_users()
    user_updated = False
    updated_user_obj = None

    for user in users:
        if user.get('id') == user_id:
            try:
                current_checks = int(user.get('checksCount', "0"))
                user['checksCount'] = str(current_checks + 1)
                user_updated = True
                updated_user_obj = user
                # print(f"DEBUG: checksCount para {user_id} actualizado a {user['checksCount']}")
            except ValueError:
                print(f"Error: 'checksCount' para el usuario {user_id} no es un número válido.")
                return None # O manejar el error de otra forma
            break
    
    if user_updated:
        save_users(users)
        # print(f"checksCount para usuario ID '{user_id}' incrementado.")
        return updated_user_obj
    else:
        print(f"Error: Usuario con ID '{user_id}' no encontrado para incrementar checksCount.")
        return None
    # --- FIN DE SECCIÓN CRÍTICA ---

def add_available_process_programation(user_id: str, add_process_amount: int):
    """Suma 'add_process_amount' a 'processProgramationAvalaible' en el plan del usuario."""
    users = load_users()
    user_updated = False
    updated_user_obj = None

    for user in users:
        if user.get('id') == user_id:
            if 'plan' in user and isinstance(user['plan'], dict):
                try:
                    current_available = int(user['plan'].get('processProgramationAvalaible', "0"))
                    user['plan']['processProgramationAvalaible'] = str(current_available + add_process_amount)
                    user_updated = True
                    updated_user_obj = user
                except ValueError:
                    print(f"Error: 'processProgramationAvalaible' para el usuario {user_id} no es un número válido.")
                    return None
            else:
                print(f"Error: Usuario {user_id} no tiene una estructura de 'plan' válida.")
                return None
            break
            
    if user_updated:
        save_users(users)
        print(f"processProgramationAvalaible para usuario ID '{user_id}' actualizado a '{updated_user_obj['plan']['processProgramationAvalaible']}'.")
        return updated_user_obj
    else:
        print(f"Error: Usuario con ID '{user_id}' no encontrado.")
        return None

def add_process_finished_history(user_id: str, process_finished_entry: str):
    """Agrega una entrada al array 'processFinishedHistory' del usuario."""
    users = load_users()
    user_updated = False
    updated_user_obj = None

    for user in users:
        if user.get('id') == user_id:
            if 'processFinishedHistory' not in user or not isinstance(user['processFinishedHistory'], list):
                user['processFinishedHistory'] = [] # Inicializa si no existe o es incorrecto
            
            user['processFinishedHistory'].append(process_finished_entry)
            
            # Opcional: incrementar también el contador 'processfinished'
            try:
                current_finished_count = int(user.get('processfinished', "0"))
                user['processfinished'] = str(current_finished_count + 1)
            except ValueError:
                 print(f"Advertencia: 'processfinished' para el usuario {user_id} no es un número válido, no se incrementará.")


            user_updated = True
            updated_user_obj = user
            break
            
    if user_updated:
        save_users(users)
        print(f"Entrada '{process_finished_entry}' agregada a processFinishedHistory para usuario ID '{user_id}'.")
        return updated_user_obj
    else:
        print(f"Error: Usuario con ID '{user_id}' no encontrado.")
        return None

def login_user(identifier: str, password_attempt: str):
    """
    Valida el inicio de sesión de un usuario.

    Args:
        identifier (str): El username o email del usuario.
        password_attempt (str): La contraseña ingresada por el usuario.

    Returns:
        bool: True si las credenciales son correctas, False en caso contrario.
    """
    users = load_users()
    if not users: # Si no hay usuarios o el archivo no se pudo cargar
        return False
    print(identifier)
    print(users)
    for user in users:
        # Verificar si el identificador coincide con el username O el email
        is_identifier_match = (user.get('username') == identifier or 
                               user.get('email') == identifier)
        
        if is_identifier_match:
            # Si el identificador coincide, verificar la contraseña
            if user.get('password') == password_attempt:
                print(f"Login exitoso para el usuario: {user.get('username')}")
                return user # Credenciales correctas
            else:
                # Identificador correcto, pero contraseña incorrecta
                print(f"Contraseña incorrecta para el identificador: {identifier}")
                return False # No seguir buscando si el identificador ya coincidió
                             # (asumiendo que username/email son únicos)
    
    # Si el bucle termina, significa que el identificador no se encontró
    print(f"Usuario/Email '{identifier}' no encontrado.")
    return False


# --- Ejemplo de uso ---
# if __name__ == "__main__":
#     # Crear el archivo users.json con datos iniciales si no existe
#     if not os.path.exists(USERS_JSON_FILE):
#         initial_users = [
#             {
#                 "id": "0001",
#                 "username": "visanow",
#                 "name": "Visa",
#                 "surname": "Now",
#                 "position": "Empresa",
#                 "email": "info@visanow.com",
#                 "src": "wanna1.png",
#                 "isOnline": True,
#                 "isReply": True,
#                 "color": "primary",
#                 "password": "@ABC123",
#                 "checksCount": "0",
#                 "processfinished": "0",
#                 "processFinishedHistory": [],
#                 "plan": {
#                     "type": "processCount",
#                     "processProgramationAvalaible": "10",
#                     "processChekingAvalaible": "25",
#                     "planExpiration": "05-15-2026",
#                     "planRenewed": "05-01-2025",
#                     "planStarted": "05-01-2025"
#                 }
#             }
#         ]
#         save_users(initial_users)
#         print(f"{USERS_JSON_FILE} creado con datos iniciales.")

#     # 1. Obtener todos los usuarios
#     print("\n--- Todos los usuarios ---")
#     all_users = get_all_users()
#     for u in all_users:
#         print(f"ID: {u['id']}, Username: {u['username']}")

#     # 2. Crear un nuevo usuario
#     print("\n--- Crear usuario ---")
#     new_user_data = {
#         # "id": "0002", # Podemos dejar que se genere automáticamente
#         "username": "johndoe",
#         "name": "John",
#         "surname": "Doe",
#         "position": "Developer",
#         "email": "john.doe@example.com",
#         "src": "avatar.png",
#         "isOnline": False,
#         "isReply": False,
#         "color": "secondary",
#         "password": "SecurePassword123",
#         # "checksCount": "0", # Se establecerá por defecto
#         # "processfinished": "0", # Se establecerá por defecto
#         # "processFinishedHistory": [], # Se establecerá por defecto
#         "plan": { # Si no se provee, se usará el default
#             "type": "basic",
#             "processProgramationAvalaible": "5",
#             "processChekingAvalaible": "10",
#             "planExpiration": "12-31-2025",
#             "planRenewed": "01-01-2025",
#             "planStarted": "01-01-2025"
#         }
#     }
#     created_user = create_user(new_user_data)
#     if created_user:
#         user_0002_id = created_user['id'] # Guardamos el ID generado
#         print(f"Usuario creado: {created_user['username']} con ID {user_0002_id}")

#         # Intentar crear un usuario con ID duplicado (si el anterior no se autogeneró)
#         # create_user(new_user_data) # Descomentar para probar el error de ID duplicado si se usó "0002"


#     # 3. Obtener un usuario por ID
#     print("\n--- Obtener usuario por ID (0001) ---")
#     user1 = get_user_by_id("0001")
#     if user1:
#         print(f"Usuario encontrado: {user1['username']}, Email: {user1['email']}")
#     else:
#         print("Usuario 0001 no encontrado.")

#     # 4. Actualizar un campo específico (update_user_field)
#     print("\n--- Actualizar campo 'email' del usuario 0001 ---")
#     updated_user = update_user_field("0001", "email", "new.info@visanow.com")
#     if updated_user:
#         print(f"Email actualizado: {updated_user['email']}")
    
#     print("\n--- Actualizar campo anidado 'plan.type' del usuario 0001 ---")
#     updated_user_plan = update_user_field("0001", "plan.type", "premium")
#     if updated_user_plan:
#         print(f"Plan Type actualizado: {updated_user_plan['plan']['type']}")

#     # 5. Incrementar checksCount para usuario 0001 (simulando múltiples llamadas)
#     print("\n--- Incrementar checksCount para usuario 0001 (3 veces) ---")
#     for _ in range(3):
#         u = add_checks_count("0001")
#         if u:
#             print(f"checksCount ahora es: {u['checksCount']}")
#         else:
#             print("Fallo al incrementar checksCount para 0001")
#             break
    
#     user1_after_checks = get_user_by_id("0001")
#     if user1_after_checks:
#         print(f"Valor final de checksCount para 0001: {user1_after_checks['checksCount']}")


#     # 6. Sumar a processProgramationAvalaible para usuario 0001
#     print("\n--- Sumar 5 a processProgramationAvalaible para usuario 0001 ---")
#     u = add_available_process_programation("0001", 5)
#     if u:
#         print(f"processProgramationAvalaible ahora es: {u['plan']['processProgramationAvalaible']}")

#     # 7. Agregar al historial de procesos finalizados para usuario 0001
#     print("\n--- Agregar a processFinishedHistory para usuario 0001 ---")
#     u = add_process_finished_history("0001", "Proceso_A_completado_2024-07-27_10:00")
#     u = add_process_finished_history("0001", "Proceso_B_completado_2024-07-27_10:05")
#     if u:
#         print(f"processFinishedHistory ahora tiene {len(u['processFinishedHistory'])} entradas.")
#         print(f"Contador processfinished ahora es: {u['processfinished']}")


#     # 8. Actualizar un usuario completamente (update_user_full)
#     if created_user: # Solo si el usuario "0002" (o autogenerado) fue creado
#         print(f"\n--- Actualizar completamente el usuario ID {user_0002_id} ---")
#         user_to_update_data = get_user_by_id(user_0002_id) # Obtenemos los datos actuales
#         if user_to_update_data:
#             user_to_update_data['name'] = "Jonathan"
#             user_to_update_data['isOnline'] = True
#             user_to_update_data['plan']['planExpiration'] = "01-01-2027"
            
#             # No es necesario pasar el ID dentro de user_to_update_data, 
#             # la función lo manejará usando el user_id provisto.
#             # Si se pasa, debe coincidir.
            
#             fully_updated_user = update_user_full(user_0002_id, user_to_update_data)
#             if fully_updated_user:
#                 print(f"Usuario {user_0002_id} completamente actualizado. Nuevo nombre: {fully_updated_user['name']}, Online: {fully_updated_user['isOnline']}")
#         else:
#             print(f"No se encontró el usuario {user_0002_id} para la actualización completa.")


#     # 9. Eliminar un usuario
#     if created_user: # Solo si el usuario "0002" (o autogenerado) fue creado
#         print(f"\n--- Eliminar usuario ID {user_0002_id} ---")
#         if delete_user(user_0002_id):
#             print(f"Usuario {user_0002_id} eliminado exitosamente.")
#             # Verificar que ya no existe
#             if not get_user_by_id(user_0002_id):
#                 print(f"Verificación: Usuario {user_0002_id} ya no se encuentra.")
#         else:
#             print(f"No se pudo eliminar el usuario {user_0002_id}.")
    
#     print("\n--- Todos los usuarios al final ---")
#     all_users_final = get_all_users()
#     for u_final in all_users_final:
#         print(f"ID: {u_final['id']}, Username: {u_final['username']}, Checks: {u_final['checksCount']}, History: {len(u_final['processFinishedHistory'])}")