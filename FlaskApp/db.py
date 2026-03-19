# from pymongo import MongoClient
# import subprocess
# import psutil
# import signal
# import time
# import os

# # ==========================
# # 🔧 CONFIGURACIÓN
# # ==========================

# # USE_LOCAL_DB = True  # True = Mongo local, False = Mongo Atlas remoto
# LOCAL_DB_PATH = "/usr/local/var/mongodb"
# LOCAL_PORT = 27017

# # Si luego usas Atlas:
# # MONGO_URI = "mongodb+srv://<usuario>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority"
# MONGO_URI = os.environ.get("MONGO_URI")
# USE_LOCAL_DB = os.environ.get("USE_LOCAL_DB", "false").lower() in ("1","true","yes")

# mongo_process = None


# # ==========================
# # ⚙️ CONTROL DE MONGODB LOCAL
# # ==========================

# def is_mongo_running():
#     """Verifica si el proceso mongod está activo."""
#     for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
#         try:
#             name = proc.info.get('name', '')
#             cmdline = proc.info.get('cmdline', [])
#             if not isinstance(cmdline, (list, tuple)):
#                 cmdline = []
#             if "mongod" in name or any("mongod" in str(arg) for arg in cmdline):
#                 return True
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             continue
#     return False


# def start_mongo():
#     """Inicia MongoDB local si no está corriendo."""
#     global mongo_process
#     if not USE_LOCAL_DB:
#         return  # No aplica si usamos Atlas

#     if is_mongo_running():
#         print("✅ MongoDB local ya está corriendo.")
#         return

#     print("🚀 Iniciando MongoDB local...")
#     mongo_process = subprocess.Popen(
#         ["mongod", "--dbpath", LOCAL_DB_PATH],
#         stdout=subprocess.DEVNULL,
#         stderr=subprocess.DEVNULL
#     )
#     time.sleep(2)
#     print("✅ MongoDB local iniciado correctamente.")


# def stop_mongo():
#     """Detiene MongoDB solo si fue iniciado por este script."""
#     global mongo_process
#     if not USE_LOCAL_DB:
#         return

#     if mongo_process and mongo_process.poll() is None:
#         print("🛑 Deteniendo MongoDB local...")
#         mongo_process.send_signal(signal.SIGINT)
#         mongo_process.wait(timeout=5)
#         print("✅ MongoDB detenido correctamente.")
#     else:
#         print("ℹ️ MongoDB no fue iniciado por este script o ya está cerrado.")


# # ==========================
# # 💾 CONEXIÓN A LA BASE DE DATOS
# # ==========================

# def connect_db():
#     """Conecta con MongoDB local o remoto."""
#     if USE_LOCAL_DB:
#         start_mongo()
#         # client = MongoClient(f"mongodb://localhost:{LOCAL_PORT}/")
#         client = MongoClient(MONGO_URI)
#         print("✅ Conectado a MongoDB local.")
#     else:
#         # client = MongoClient(MONGO_URI)
#         client = MongoClient("mongodb://mongo:27017/")
#         print("✅ Conectado a MongoDB Atlas remoto.")

#     db = client["visa_db"]
#     return db


# # Inicializar conexión global
# db = connect_db()
# users_collection = db["users"]
# processes_collection = db["processes"]
