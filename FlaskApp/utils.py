import os
from typing import List

def get_stop_month(month: str) -> List[str]:
    stop_month_dict = {
        # Claves en español
        'enero':        ["January", "january", "Enero", "enero"],
        'febrero':      ["February", "february", "Febrero", "febrero"],
        'marzo':        ["March", "march", "Marzo", "marzo"],
        'abril':        ["April", "april", "Abril", "abril"],
        'mayo':         ["May", "may", "Mayo", "mayo"],
        'junio':        ["June", "june", "Junio", "junio"],
        'julio':        ["July", "july", "Julio", "julio"],
        'agosto':       ["August", "august", "Agosto", "agosto"],
        'septiembre':   ["September", "september", "Septiembre", "septiembre"],
        'octubre':      ["October", "october", "Octubre", "octubre"],
        'noviembre':    ["November", "november", "Noviembre", "noviembre"],
        'diciembre':    ["December", "december", "Diciembre", "diciembre"],
        
        # Claves en inglés
        'january':      ["January", "january", "Enero", "enero"],
        'february':     ["February", "february", "Febrero", "febrero"],
        'march':        ["March", "march", "Marzo", "marzo"],
        'april':        ["April", "april", "Abril", "abril"],
        'may':          ["May", "may", "Mayo", "mayo"],
        'june':         ["June", "june", "Junio", "junio"],
        'july':         ["July", "july", "Julio", "julio"],
        'august':       ["August", "august", "Agosto", "agosto"],
        'september':    ["September", "september", "Septiembre", "septiembre"],
        'october':      ["October", "october", "Octubre", "octubre"],
        'november':     ["November", "november", "Noviembre", "noviembre"],
        'december':     ["December", "december", "Diciembre", "diciembre"]
    }
    # Convertimos la entrada a minúsculas para poder buscar en el diccionario
    key = month.lower()
    return stop_month_dict.get(key, [])

# LOGS ===============================================
def get_log_filename(email: str) -> str:
    """Genera el path del archivo de log en la carpeta 'logs' usando el email."""
    filename = f"{email.replace('@', '_at_')}.log"
    return os.path.join("logs", filename)

def reverse_readline(filename, buf_size=8192):
    """
    Generador que devuelve las líneas de un archivo en orden inverso.
    Lee el archivo en bloques para no cargarlo completamente en memoria.
    """
    with open(filename, 'rb') as fh:
        fh.seek(0, os.SEEK_END)
        file_size = fh.tell()
        buffer = bytearray()
        pos = file_size
        while pos > 0:
            # Leer en bloques de buf_size
            read_size = buf_size if pos >= buf_size else pos
            pos -= read_size
            fh.seek(pos)
            data = fh.read(read_size)
            buffer[0:0] = data
            # Dividir el buffer por saltos de línea
            while b'\n' in buffer:
                newline_index = buffer.rfind(b'\n')
                line = buffer[newline_index+1:]
                yield line.decode('utf-8', errors='replace')
                buffer = buffer[:newline_index]
        if buffer:
            yield buffer.decode('utf-8', errors='replace')


def get_paginated_logs(filename: str, offset: int, limit: int):
    """
    Utiliza reverse_readline para obtener los logs en orden descendente (más recientes primero)
    sin cargar el archivo completo.
    
    Retorna:
      - logs: una lista con 'limit' líneas a partir de 'offset'
      - total: número total de líneas leídas (hasta donde se pudo contar)
    """
    logs = []
    total = 0
    for line in reverse_readline(filename):
        if total < offset:
            total += 1
            continue
        if len(logs) < limit:
            logs.append(line)
        total += 1
    return logs, total