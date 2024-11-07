from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from userCredentials import USER_EMAIL, USER_PASSWORD

url = "https://ais.usvisa-info.com/es-ec/niv/schedule/52492462/appointment"

def verificar_cita():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Ejecuta el navegador en modo headless (sin interfaz gráfica)
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--no-sandbox")


    driver_path = "./chromedriver.exe"
    service = Service(driver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        time.sleep(5)
        current_url = driver.current_url
        login_url = "https://ais.usvisa-info.com/es-ec/niv/users/sign_in"

        if current_url == login_url:
            print("El navegador ha sido redireccionado a la página de inicio de sesión.")
            login(driver)

            time.sleep(5)
            current_url = driver.current_url

            if current_url == url:
                print("Redirección exitosa a la página de citas.")
                check_dates(driver)
            else:
                errorController("Hubo fallo al redireccionar después de inicio de sesión.")
        else:
            print("El navegador está en la página de citas o en otra página diferente.")
            check_dates(driver)
    except Exception as e:
        errorController(e)
    finally:
        driver.quit()




def errorController(e):
    print(f"Error: {e}")

def login(driver):
    try:
        # Verificar y hacer clic en el botón "OK" si está presente
        try:
            ok_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ui-button"))
            )
            ok_button.click()
            print("Botón OK encontrado y clickeado.")
        except:
            print("No se encontró el botón OK.")

        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "user_email"))
        )
        email_input.send_keys(USER_EMAIL)
        password_input = driver.find_element(By.ID, "user_password")
        password_input.send_keys(USER_PASSWORD)

        policy_checkbox = driver.find_element(By.ID, "policy_confirmed")
        driver.execute_script("arguments[0].click();", policy_checkbox)


        submit_button = driver.find_element(By.NAME, "commit")
        submit_button.click()
    except Exception as e:
        errorController(f"Error durante el proceso de inicio de sesión: {e}")

def check_dates(driver):
    print("Verificando las fechas disponibles de citas...")
    # Implementación pendiente
