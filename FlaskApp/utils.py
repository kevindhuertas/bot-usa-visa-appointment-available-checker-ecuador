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
