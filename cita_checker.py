from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

def verificar_cita():
    chrome_service = Service("./chromedriver.exe") 
    driver = webdriver.Chrome(service=chrome_service)
    try:
        appointment_url = "https://ais.usvisa-info.com/es-ec/niv/schedule/52492462/appointment"
        driver.get(appointment_url)
        time.sleep(5)  
        current_url = driver.current_url
        login_url = "https://ais.usvisa-info.com/es-ec/niv/users/sign_in" 
        if current_url == login_url:
            print("Redirigido a la página de inicio de sesión.")
        else:
            print("Página de citas abierta correctamente.")
             
    finally:
        driver.quit()
