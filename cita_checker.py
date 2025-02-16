import sys
from selenium import webdriver
import platform
import logging
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import time
from email_alert import EmailAlert
from page_credentials import USER_EMAIL, USER_PASSWORD

url = "https://ais.usvisa-info.com/es-ec/niv/schedule/52492462/appointment"
alert_sent = False
location = '';
pageLoadTime = 10;
allowed_location_to_save_appointment = ["Quito"]
allowed_months_to_save_appointment = ["February", "March", "Febrero", "Marzo"]
stop_month = ["May", "Mayo"]

def verificar_cita():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecuta el navegador en modo headless (sin interfaz gráfica)
    chrome_options.add_argument("--disable-gpu")  # Necesario para algunos entornos headless
    chrome_options.add_argument("--no-sandbox")  # Evita errores en contenedores
    chrome_options.add_argument("--disable-dev-shm-usage")  # Mejora rendimiento en modo headless
    chrome_options.add_argument("--disable-extensions")  # Nueva opción para mejor rendimiento

    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument("--remote-debugging-port=9222")

    # Detectar sistema operativo
    if platform.system() == "Windows":
        driver_path = "./chromedriver.exe"
    elif platform.system() == "Darwin":  # macOS
        driver_path = "./chromedriver"
    else:
        raise Exception("Sistema operativo no soportado. Solo Windows y macOS son compatibles.")

    # Configurar el servicio de ChromeDriver
    service = Service(driver_path)

    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        time.sleep(pageLoadTime)
        current_url = driver.current_url
        login_url = "https://ais.usvisa-info.com/es-ec/niv/users/sign_in"

        if current_url == login_url:
            print("El navegador ha sido redireccionado a la página de inicio de sesión.")
            login(driver)


            location_select_id = "appointments_consulate_appointment_facility_id"
            WebDriverWait(driver, pageLoadTime).until(
                EC.presence_of_element_located((By.ID, location_select_id))
            )

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
        errorController(f"Error crítico: {str(e)}")
    finally:
        driver.quit()





def errorController(e):
    print(f"Error: {e}")

def login(driver):
    try:
        try:
            ok_button = WebDriverWait(driver, pageLoadTime).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ui-button"))
            )
            ok_button.click()
            print("Botón OK encontrado y clickeado.")
        except:
            print("No se encontró el botón OK.")

        email_input = WebDriverWait(driver, pageLoadTime).until(
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
    global alert_sent,location
    try:
        logging.info("Check_date() running")
        location_select_id = "appointments_consulate_appointment_facility_id"
        date_input_id = "appointments_consulate_appointment_date"
        first_group_class = "ui-datepicker-group-first"
        next_button_class = "ui-datepicker-next"

        # First location
        location = "Quito";
        location_select = WebDriverWait(driver, pageLoadTime).until(
            EC.presence_of_element_located((By.ID, location_select_id))
        )
        location_select.click()
        time.sleep(1) 
        options = location_select.find_elements(By.TAG_NAME, "option")
        for option in options:
            if option.text == location:
                option.click()
                print(f"Cambio de locacion a {option.text}")
                break
        time.sleep(3)  
        verify_dates_until_june(driver, date_input_id, first_group_class, next_button_class, stop_month)

        # reset date_pciker and alert
        alert_sent = False
 
        driver.find_element(By.TAG_NAME, "body").click()
        driver.find_element(By.ID, "header").click()

        #SEGUNDA LOCACION
        location = "Guayaquil";
        location_select = WebDriverWait(driver, pageLoadTime).until(
            EC.presence_of_element_located((By.ID, location_select_id))
        )
        location_select.click()
        time.sleep(1) 
        options = location_select.find_elements(By.TAG_NAME, "option")
        for option in options:
            if option.text == location:
                option.click()
                print(f"Cambio de locacion a {option.text}")
                break
        time.sleep(3)  
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
            if(alert_sent): break
            first_group = driver.find_element(By.CLASS_NAME, first_group_class)
            current_month = first_group.find_element(By.CLASS_NAME, "ui-datepicker-month").text
            if current_month in stop_month:
                # print(f"Mes de {current_month} alcanzado, terminando la verificación.")
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
        # print(f"Verificando el mes: {month}")

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
                        
                        #save_appointment
                        if month in allowed_months_to_save_appointment:
                            if location in allowed_location_to_save_appointment:
                                a_tag[0].click()
                                autoSelectDate(driver,month,day_number)

    except Exception as e:
        errorController(f"Error durante la verificación del grupo de calendario: {e}")


def alert_available_date(month, day):
    global alert_sent
    if(alert_sent == False):
        alert_system = EmailAlert()
        alert_system.send_email_alert("CITA DISPONIBLE:",month, day,location)
        logging.info(f"EMAIL ALERT : Fecha disponible: {day} de {month} en {location}")
        alert_sent = True


def autoSelectDate(driver,month,day):
    try:
        time.sleep(4)
        # Dar click en el select de horarios de citas
        select_element = driver.find_element(By.ID, "appointments_consulate_appointment_time")
        select_element.click()
        time.sleep(3)
        # Obtener todas las opciones disponibles dentro del select
        options = select_element.find_elements(By.TAG_NAME, "option")
        time.sleep(1)

        # Verificar que exista al menos una segunda opción
        if len(options) < 2:
            print("No hay suficientes opciones disponibles en el select.")
            time.sleep(3)
            select_element = driver.find_element(By.ID, "appointments_consulate_appointment_time")
            select_element.click()
            time.sleep(15)
            # Obtener todas las opciones disponibles dentro del select
            options = select_element.find_elements(By.TAG_NAME, "option")
            time.sleep(1)
            if len(options) < 2:
                return
        # Seleccionar la segunda opción
       
        options[1].click()

        # Dar click en el botón de envío (input con id appointments_submit)
        submit_button = driver.find_element(By.ID, "appointments_submit")
        submit_button.click()

        time.sleep(1)



        # Dar click en el enlace (a) con la clase "button alert"
        # Se utiliza un selector CSS para combinar ambas clases
        #CUIDADO QUE ESCOGE CITA
        alert_button = driver.find_element(By.CSS_SELECTOR, "a.button.alert")
        alert_button.click()
        
        time.sleep(10)
        logging.info(f"FECHA SELECCIONADA Y ENVIADA {month} el {day} en {location}")
        alert_system = EmailAlert()
        alert_system.send_email_alert("CITA AUTO PROGRAMADA! ",month, day,location)
        time.sleep(45)
        # Forzar el cierre del programa
        sys.exit()

    except Exception as e:
        errorController(f"Error en autoSelectDate: {e}")
