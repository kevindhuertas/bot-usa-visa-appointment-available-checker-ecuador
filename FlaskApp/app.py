import os
from flask import Flask, request, jsonify
from utils import get_log_filename, get_paginated_logs
from process_manager import start_process, stop_process, get_process_status
from models import add_process, get_process_by_email, update_process, delete_process, list_processes
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

@app.route('/processes', methods=['GET'])
def get_processes():
    # return jsonify({"message": "CORS habilitado correctamente"}), 200
    # Devuelve la lista de procesos con su estado actualizado
    processes = list_processes()
    # Actualizar el estado de cada proceso, por ejemplo, con psutil o comprobando el PID
    for proc in processes:
        proc['active'] = get_process_status(proc.get('pid'))
    return jsonify(processes), 200

@app.route('/processes', methods=['POST'])
def create_process():
    data = request.json
    # Validar que se envíen todos los campos requeridos
    required_fields = ["USER_EMAIL", "USER_PASSWORD", "allowed_location_to_save_appointment",
                       "allowed_months_to_save_appointment", "stop_month"]
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
    # Guarda la configuración en el JSON
    add_process(data)
    return jsonify(data), 201

@app.route('/processes/<user_email>', methods=['PUT'])
def edit_process(user_email):
    data = request.json
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


if __name__ == '__main__':
    app.run(debug=True,port=5001)
