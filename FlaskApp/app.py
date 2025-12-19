import os
from flask import Flask, request, jsonify
from db import connect_db, stop_mongo, users_collection
from controllers.userController import get_user_by_id, login_user
from utils import get_log_filename, get_paginated_logs
from process_manager import start_process, stop_process, get_process_status
from models import add_process, get_process_by_email, update_process, delete_process, list_processes
from flask_cors import CORS
import json
import atexit

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000","http://127.0.0.1:5001","http://localhost:5001"])

@app.route('/processes', methods=['GET'])
def get_processes():
    user_id = request.args.get('user_id') # recoger ?user_id=123 del frontend
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    # return jsonify({"message": "CORS habilitado correctamente"}), 200
    # Devuelve la lista de procesos con su estado actualizado
    processes = list_processes()
    user_processes = [proc for proc in processes if proc.get('user_id') == user_id]
    # Actualizar el estado de cada proceso, por ejemplo, con psutil o comprobando el PID
    for proc in user_processes:
        proc['active'] = get_process_status(proc.get('pid'))
    return jsonify(user_processes), 200

@app.route('/processes', methods=['POST'])
def create_process():
    data = request.json
    # Validar que se envíen todos los campos requeridos
    required_fields = ["USER_EMAIL", "USER_PASSWORD", "allowed_location_to_save_appointment",
                       "allowed_months_to_save_appointment", "stop_month","user_id","appoinment_id"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field {field}"}), 400
    #Verificar que no se duplique
    if(get_process_by_email(data['USER_EMAIL']) != None):
        return jsonify({"error": f"{data['USER_EMAIL']} already exist"}), 400
    # Inicia el proceso mediante subprocess y obtiene el PID
    pid = start_process(data)
    data['pid'] = pid
    data['status'] = 'active'
    data['last_Error'] = ''
    data['last_check'] = ''
    add_process(data)
    return jsonify(data), 201

@app.route('/processes/<user_email>', methods=['PUT'])
def edit_process(user_email):
    data = request.json
    # required_fields = ["USER_EMAIL", "USER_PASSWORD", "allowed_location_to_save_appointment",
    #                    "allowed_months_to_save_appointment", "stop_month","user_id","appoinment_id"]
    # for field in required_fields:
    #     if field not in data:
    #         return jsonify({"error": f"Missing field {field}"}), 400
    print(f"PUT: {data}")
    # Solo se permite editar si el proceso está inactivo
    process = update_process(user_email, data)
    if not process:
        return jsonify({"error": "No se pudo editar. Asegúrate que el proceso esté inactivo."}), 400
    # Reinicia el proceso con la nueva configuración
    pid = start_process(data)
    process['pid'] = pid
    process['status'] = 'active'
    update_process(user_email, process)
    return jsonify(process), 200

@app.route('/processes/<user_email>/stop', methods=['POST'])
def stop_process_endpoint(user_email):
    # Detener el proceso activo
    process = stop_process(user_email)
    if not process:
        return jsonify({"error": "Proceso no encontrado o ya inactivo"}), 400
    return jsonify(process), 200

@app.route('/processes/<user_email>', methods=['DELETE'])
def delete_process_endpoint(user_email):
    # Solo permite eliminar si el proceso está inactivo
    result = delete_process(user_email)
    if not result:
        return jsonify({"error": "No se pudo eliminar. Verifica que el proceso esté inactivo."}), 400
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

# USER =====================================================
@app.route('/auth/login', methods=['POST'])
def login_endpoint():
    """
    Endpoint para el inicio de sesión.
    Espera un JSON con "identifier" (username o email) y "password".
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No se enviaron datos JSON."}), 400
    
    identifier = data.get('identifier')
    password = data.get('password')

    if not identifier or not password:
        return jsonify({"error": "Faltan 'identifier' o 'password' en la solicitud."}), 400

    authenticated_user = login_user(identifier, password)

    if authenticated_user:
        # En una aplicación real, aquí generarías y devolverías un token JWT
        # Por ahora, solo devolvemos los datos del usuario (sin contraseña)
        return jsonify({
            "message": "Login exitoso.",
            "user": authenticated_user #authenticated_user ya no tiene la contraseña
        }), 200
    else:
        return jsonify({"error": "Credenciales inválidas."}), 401


@app.route('/users/<user_id>', methods=['GET'])
def get_user_endpoint(user_id: str):
    """
    Endpoint para recuperar la información de un usuario por su ID.
    No devuelve la contraseña.
    """
    user = get_user_by_id(user_id)
    
    if user:
        user_data_to_return = user.copy()
        if 'password' in user_data_to_return: # Asegurarse de no enviar la contraseña
            del user_data_to_return['password']
        return jsonify(user_data_to_return), 200
    else:
        return jsonify({"error": "Usuario no encontrado."}), 404


@app.route("/db")
def ver_datos():
    print("ver ver_datos")
    users = list(users_collection.find({}, {"_id": 0}))  # sin mostrar el ObjectId
    return jsonify(users)


if __name__ == '__main__':
    atexit.register(stop_mongo) #Termina servidor mongo db
    app.run(debug=True,port=5001)
