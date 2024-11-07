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
    try:
        # Variables
        location_select_id = "appointments_consulate_appointment_facility_id"
        date_input_id = "appointments_consulate_appointment_date"
        first_group_class = "ui-datepicker-group-first"
        next_button_class = "ui-datepicker-next"
        stop_month = ["June", "Junio"]

        location_select = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, location_select_id))
        )
        location_select.send_keys("Quito")
        time.sleep(3)  
        verify_dates_until_june(driver, date_input_id, first_group_class, next_button_class, stop_month)


        print("Cambiando a la ubicación Guayaquil...")
        location_select.send_keys("Guayaquil")
        driver.find_element(By.TAG_NAME, "body").click()
        time.sleep(5) 
        verify_dates_until_june(driver, date_input_id, first_group_class, next_button_class, stop_month)

    except Exception as e:
        errorController(f"Error durante la verificación de fechas: {e}")

def verify_dates_until_june(driver, date_input_id, first_group_class, next_button_class, stop_month):
    while True:
        try:
            # Hacer clic en el input para desplegar el calendario
            date_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, date_input_id))
            )
            driver.execute_script("arguments[0].click();", date_input)

            check_calendar_group(driver, first_group_class)
            first_group = driver.find_element(By.CLASS_NAME, first_group_class)
            current_month = first_group.find_element(By.CLASS_NAME, "ui-datepicker-month").text
            if current_month in stop_month:
                print(f"Mes de {current_month} alcanzado, terminando la verificación.")
                break

            # Pasar al siguiente mes (doble clic en el botón "next" para asegurarnos de avanzar mes a mes)
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, next_button_class))
            )
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)
        except Exception as e:
            errorController(f"Error durante la verificación de fechas: {e}")
            break

def check_calendar_group(driver, group_class):
    try:
        # Obtener el grupo del calendario
        calendar_group = driver.find_element(By.CLASS_NAME, group_class)
        month = calendar_group.find_element(By.CLASS_NAME, "ui-datepicker-month").text
        print(f"Verificando el mes: {month}")

        # Obtener los días del mes
        tbody = calendar_group.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")

        for row in rows:
            days = row.find_elements(By.TAG_NAME, "td")
            for day in days:
                if "ui-datepicker-unselectable" not in day.get_attribute("class"):
                    a_tag = day.find_elements(By.TAG_NAME, "a")
                    if a_tag:
                        day_number = a_tag[0].text
                        alert_available_date(month, day_number)
    except Exception as e:
        errorController(f"Error durante la verificación del grupo de calendario: {e}")

def alert_available_date(month, day):
    print(f"Fecha disponible encontrada: {day} de {month}")
