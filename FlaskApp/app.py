import os
from flask import Flask, app, request, jsonify
# from db import connect_db, stop_mongo, users_collection
from controllers.userController import get_user_by_id, login_user
from utils import get_log_filename, get_paginated_logs
from process_manager import start_process, stop_process, get_process_status
from models import add_process, update_process, delete_process, list_processes
from flask_cors import CORS
# import json
# import atexit
from supabase_client import check_connection
import logging

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000","http://127.0.0.1:5001","http://localhost:5001","https://puntovisas.com","https://app.puntovisas.com","*"])

# Check Supabase connection on startup
if check_connection():
    print("Supabase connection successful.")
else:
    print("WARNING: Supabase connection failed.")


@app.route("/")
def startapi():
    return "API funcionando 🚀"

@app.route("/test")
def home():
    return jsonify({"message": "Hola desde Punto Visas!"})

@app.route('/processes', methods=['GET'])
def get_processes():
    user_id = request.args.get('user_id') # recoger ?user_id=123 del frontend
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    # return jsonify({"message": "CORS habilitado correctamente"}), 200
    # Devuelve la lista de procesos con su estado actualizado
    processes = list_processes()
    user_processes = [proc for proc in processes if proc.get('user_id') == user_id]
    # Actualizar el estado de cada proceso, por ejemplo, 
    for proc in user_processes:
        proc['active'] = get_process_status(proc.get('pid'))
    return jsonify(user_processes), 200

import uuid

@app.route('/processes', methods=['POST'])
def create_process():
    data = request.json
    # Validar que se envíen todos los campos requeridos
    required_fields = ["USER_EMAIL", "USER_PASSWORD", "allowed_location_to_save_appointment",
                       "allowed_months_to_save_appointment", "stop_month","user_id","appoinment_id"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field {field}"}), 400
    
    # Generate ID if not present
    if 'process_id' not in data and 'id' not in data:
        data['process_id'] = str(uuid.uuid4())
    elif 'id' in data and 'process_id' not in data:
        data['process_id'] = data['id']
        
    from models import get_process_by_email_and_user
    #Verificar que no se duplique
    if(get_process_by_email_and_user(data['USER_EMAIL'], data['user_id']) != None):
        return jsonify({"error": f"El email {data['USER_EMAIL']} ya existe en tus procesos"}), 400
    # Inicia el proceso mediante subprocess y obtiene el PID
    pid = start_process(data)
    data['pid'] = pid
    data['status'] = 'active'
    data['last_Error'] = ''
    data['last_check'] = ''
    success, error = add_process(data)

    if not success:
        return jsonify({"error": f"Error al crear el proceso: {error}"}), 500

    return jsonify(data), 201

@app.route('/processes/<process_id>', methods=['PUT'])
def edit_process(process_id):
    data = request.json
    print(f"PUT: {data}")
    # Solo se permite editar si el proceso está inactivo
    process, error = update_process(process_id, data)
    if not process:
        return jsonify({"error": error or "No se pudo editar. Asegúrate que el proceso esté inactivo."}), 400
    # Reinicia el proceso con la nueva configuración
    pid = start_process(data)
    process['pid'] = pid
    process['status'] = 'active'
    updated_process, error = update_process(process_id, process)
    if error:
        return jsonify({"error": f"Error al actualizar el proceso después de reiniciar: {error}"}), 500
    return jsonify(process), 200

@app.route('/processes/<process_id>/stop', methods=['POST'])
def stop_process_endpoint(process_id):
    if not process_id:
        return jsonify({"error": "process_id es requerido"}), 400

    print(f"Deteniendo proceso con ID: {process_id}")

    # Detener el proceso activo
    process, error_msg = stop_process(process_id)
    
    if not process:
        return jsonify({"error": error_msg or "Proceso no encontrado"}), 400
        
    if error_msg:
        # Si hubo un error deteniendo en OS pero se actualizó en BD
        return jsonify({"process": process, "info": error_msg}), 200
        
    return jsonify(process), 200

@app.route('/processes/<process_id>', methods=['DELETE'])
def delete_process_endpoint(process_id):
    # Solo permite eliminar si el proceso está inactivo
    result, error = delete_process(process_id)
    if not result:
        return jsonify({"error": error or "No se pudo eliminar. Verifica que el proceso esté inactivo."}), 400
    return jsonify({"message": "Proceso eliminado exitosamente"}), 200
    
    
@app.route('/logs/<email>', methods=['GET'])
def get_logs(email: str):
    """
    Endpoint para obtener logs paginados para un email.
    Parámetros opcionales (query):
      - limit: número máximo de logs a retornar (default 100)
      - offset: cantidad de logs a saltar (default 0)
    Devuelve:
      - logs: lista de líneas (más recientes primero)
      - offset: valor actual de offset
      - limit: valor del límite
      - total: total de líneas contadas (hasta donde se pudo recorrer)
      - has_more: True si hay más líneas que no se retornaron
    """
    limit = request.args.get('limit', default=100, type=int)
    offset = request.args.get('offset', default=0, type=int)

    log_file = get_log_filename(email)
    if not os.path.exists(log_file):
        return jsonify({
            "logs": [],
            "offset": offset,
            "limit": limit,
            "total": 0,
            "has_more": False
        }), 200

    logs, total = get_paginated_logs(log_file, offset, limit)
    has_more = (offset + limit) < total
    return jsonify({
        "logs": logs,
        "offset": offset,
        "limit": limit,
        "total": total,
        "has_more": has_more
    }), 200
# Solo para local
if __name__ == '__main__':
    print("Iniciando app desde Main...")
    # atexit.register(stop_mongo) #Termina servidor mongo db
    # app.run(debug=True,port=5001)
    port = int(os.environ.get("PORT", 8080))
    # port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=False)


# USER =====================================================
# @app.route('/auth/login', methods=['POST'])
# def login_endpoint(): 
#     data = request.get_json()
#     if not data:
#         return jsonify({"error": "No se enviaron datos JSON."}), 400
    
#     identifier = data.get('identifier')
#     password = data.get('password')
#     if not identifier or not password:
#         return jsonify({"error": "Faltan 'identifier' o 'password' en la solicitud."}), 400
#     authenticated_user = login_user(identifier, password)
#     if authenticated_user:
#         # En una aplicación real, aquí generarías y devolverías un token JWT
#         # Por ahora, solo devolvemos los datos del usuario (sin contraseña)
#         return jsonify({
#             "message": "Login exitoso.",
#             "user": authenticated_user #authenticated_user ya no tiene la contraseña
#         }), 200
#     else:
#         return jsonify({"error": "Credenciales inválidas."}), 401


# @app.route('/users/<user_id>', methods=['GET'])
# def get_user_endpoint(user_id: str):
#     """
#     Endpoint para recuperar la información de un usuario por su ID.
#     No devuelve la contraseña.
#     """
#     user = get_user_by_id(user_id)
    
#     if user:
#         user_data_to_return = user.copy()
#         if 'password' in user_data_to_return: # Asegurarse de no enviar la contraseña
#             del user_data_to_return['password']
#         return jsonify(user_data_to_return), 200
#     else:
#         return jsonify({"error": "Usuario no encontrado."}), 404



