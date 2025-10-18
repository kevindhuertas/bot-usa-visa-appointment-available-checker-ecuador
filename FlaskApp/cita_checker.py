import sys
from typing import List
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

class AppointmentCheck:
    def __init__(self, 
                email: str,
                password: str,
                allowed_location_to_save_appointment: List[str],
                months: List[str],
                stop_month: List[str],
                blocked_days: List[str],
                logger: logging.Logger
                ): #format: ["2025-03-27","2025-03-23"]
        self.url = "https://ais.usvisa-info.com/es-ec/niv/schedule/52492462/appointment"
        self.alert_sent = False
        self.location = ''
        self.pageLoadTime = 10
        self.allowed_location_to_save_appointment = allowed_location_to_save_appointment
        self.allowed_months_to_save_appointment = months
        self.stop_month = stop_month
        self.blocked_days = blocked_days
        self.email = email
        self.password = password
        self.logger = logger

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
        if platform.system() == "Windows":
            driver_path = "./drivers/chromedriver.exe"
        elif platform.system() == "Darwin":
            driver_path = "./drivers/chromedriver"
        elif platform.system() == "Linux":
            driver_path = "./drivers/chromedriverlinux"
        else:
            raise Exception("Sistema operativo no soportado.")
        
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)


    def check(self):
        try:
            self.driver.get(self.url)
            time.sleep(self.pageLoadTime)
            current_url = self.driver.current_url
            login_url = "https://ais.usvisa-info.com/es-ec/niv/users/sign_in"

            if current_url == login_url:
                self.login()
                try:
                    WebDriverWait(self.driver, self.pageLoadTime).until(
                        EC.url_changes(login_url)
                    )
                except TimeoutException:
                    self.error_controller("Fallo en el inicio de sesión, revisar credenciales")
                    return

                current_url_after_login = self.driver.current_url
                self.print_controller("Se inició sesión exitosamente")
                location_select_id = "appointments_consulate_appointment_facility_id"
                try:
                    WebDriverWait(self.driver, self.pageLoadTime).until(
                        EC.presence_of_element_located((By.ID, location_select_id))
                    )

                except TimeoutException:
                    self.error_controller("No se encontró el elemento de ubicación (appointments_consulate_appointment).")
                    return

                
                if current_url_after_login == self.url:
                    self.check_dates()
                else:
                    self.error_controller("Hubo fallo al redireccionar después de inicio de sesión")

            else:
                self.error_controller("El programa está en la página de citas o en otra página diferente.")
        except Exception as e:
            self.error_controller(f"Error durante el proceso de inicio de sesión y redirección a verificación de citas: {e}")
        finally:
            self.driver.quit()

    def error_controller(self, e):
        self.logger.error(f"Error: {e}")

    def print_controller(self, e):
        self.logger.info(f"{e}")

    def warning_controller(self, e):
        self.logger.warning(f"{e}")

    def login(self):
        try:
            try:
                ok_button = WebDriverWait(self.driver, self.pageLoadTime).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ui-button"))
                )
                ok_button.click()
            except:
                self.print_controller("No se encontró el botón OK antes de iniciar sesión")

            email_input = WebDriverWait(self.driver, self.pageLoadTime).until(
                EC.presence_of_element_located((By.ID, "user_email"))
            )
            email_input.send_keys(self.email)
            password_input = self.driver.find_element(By.ID, "user_password")
            password_input.send_keys(self.password)

            policy_checkbox = self.driver.find_element(By.ID, "policy_confirmed")
            self.driver.execute_script("arguments[0].click();", policy_checkbox)

            submit_button = self.driver.find_element(By.NAME, "commit")
            submit_button.click()
        except Exception as e:
            self.error_controller(f"Error durante el proceso de inicio de sesión: {e}")

    def check_dates(self):
        try:
            self.print_controller("Continuando con checkeo en página de citas")
            location_select_id = "appointments_consulate_appointment_facility_id"
            date_input_id = "appointments_consulate_appointment_date"
            first_group_class = "ui-datepicker-group-first"
            next_button_class = "ui-datepicker-next"

            self.location = "Quito"
            location_select = WebDriverWait(self.driver, self.pageLoadTime).until(
                EC.presence_of_element_located((By.ID, location_select_id)))
            location_select.click()
            time.sleep(1)
            options = location_select.find_elements(By.TAG_NAME, "option")
            for option in options:
                if option.text == self.location:
                    option.click()
                    break
            time.sleep(3)
            self.verify_dates_until_june(date_input_id, first_group_class, next_button_class)

            self.alert_sent = False
            self.driver.find_element(By.TAG_NAME, "body").click()
            self.driver.find_element(By.ID, "header").click()

            self.location = "Guayaquil"
            location_select = WebDriverWait(self.driver, self.pageLoadTime).until(
                EC.presence_of_element_located((By.ID, location_select_id)))
            location_select.click()
            time.sleep(1)
            options = location_select.find_elements(By.TAG_NAME, "option")
            for option in options:
                if option.text == self.location:
                    option.click()
                    break
            time.sleep(3)
            self.verify_dates_until_june(date_input_id, first_group_class, next_button_class)

        except Exception as e:
            self.error_controller(f"Error durante la verificación de fechas de citas ")

    def verify_dates_until_june(self, date_input_id, first_group_class, next_button_class):
        while True:
            try:
                date_input = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.ID, date_input_id)))
                self.driver.execute_script("arguments[0].click();", date_input)

                self.check_calendar_group(first_group_class)
                if self.alert_sent: break
                
                first_group = self.driver.find_element(By.CLASS_NAME, first_group_class)
                current_month = first_group.find_element(By.CLASS_NAME, "ui-datepicker-month").text
                if current_month in self.stop_month:
                    # print(f"Mes de {current_month} alcanzado, terminando la verificación.")
                    break
                
                # Pasar al siguiente mes (doble clic en el botón "next" para asegurarnos de avanzar mes a mes)
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, next_button_class)))
                self.driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)
            except Exception as e:
                self.error_controller(f"Error durante la verificación diaria de fechas de citas")
                break

    def check_calendar_group(self, group_class):
        try:
            calendar_group = self.driver.find_element(By.CLASS_NAME, group_class)
            month_element = calendar_group.find_element(By.CLASS_NAME, "ui-datepicker-month")
            month = month_element.text.strip().lower()
            # print(f"Verificando el mes: {month}")
            # Obtener los días del mes
            tbody = calendar_group.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            month_map = {
                'january': '01', 'febrero': '02', 'february': '02',
                'marzo': '03', 'march': '03', 'abril': '04', 'april': '04',
                'mayo': '05', 'may': '05', 'junio': '06', 'june': '06',
                'julio': '07', 'july': '07', 'agosto': '08', 'august': '08',
                'septiembre': '09', 'september': '09', 'octubre': '10',
                'october': '10', 'noviembre': '11', 'november': '11',
                'diciembre': '12', 'december': '12'
            }

            for row in rows:
                days = row.find_elements(By.TAG_NAME, "td")
                for day in days:
                    if "ui-datepicker-unselectable" not in day.get_attribute("class"):
                        a_tag = day.find_elements(By.TAG_NAME, "a")
                        if a_tag:
                            day_number = a_tag[0].text.zfill(2)
                            current_month = month_map.get(month, '00')
                            # Crear patrón MM-DD para comparación
                            current_date = f"{current_month}-{day_number}"
                            is_blocked = any(
                                blocked_date.endswith(current_date)
                                for blocked_date in self.blocked_days
                            )
                            self.alert_available_date(month, day_number)
                            
                            if month.lower() in [m.lower() for m in self.allowed_months_to_save_appointment]:
                                if self.location.lower() in [l.lower() for l in self.allowed_location_to_save_appointment]:
                                    if not is_blocked:
                                        a_tag[0].click()
                                        # self.auto_select_date(month, day_number)
                                    else:
                                        self.warning_controller(f"Fecha bloqueada detectada, cita encontrada el: {current_date}")
                                else:
                                    self.warning_controller(f"Fecha bloqueada detectada, cita encontrada el: {current_date} en {self.location} ")
                            else:
                                self.warning_controller(f"Fecha fuera de locacion permitida, cita encontrada el: {current_date} en {self.location}")
        except Exception as e:
            self.error_controller(f"Error durante la verificación del grupo de calendario")

    def alert_available_date(self, month, day):
        if (self.alert_sent== False):
            alert_system = EmailAlert()
            alert_system.send_email_alert("CITA DISPONIBLE:", month, day, self.location)
            self.warning_controller(f"ALERTA A EMAIL: Fecha disponible el {day} de {month} en {self.location}")
            self.alert_sent = True

    def auto_select_date(self, month, day):
        try:
            time.sleep(4)
            select_element = self.driver.find_element(By.ID, "appointments_consulate_appointment_time")
            select_element.click()
            time.sleep(3)
            options = select_element.find_elements(By.TAG_NAME, "option")
            time.sleep(1)
            # Verificar que exista al menos una segunda opción
            if len(options) < 2:
                self.print_controller("No hay suficientes opciones disponibles en el select para seleccionar una cita.")
                time.sleep(3)
                select_element = self.driver.find_element(By.ID, "appointments_consulate_appointment_time")
                select_element.click()
                time.sleep(15)
                # Obtener todas las opciones disponibles dentro del select
                options = select_element.find_elements(By.TAG_NAME, "option")
                time.sleep(1)
                if len(options) < 2:
                    return

            options[1].click()
             # Dar click en el botón de envío (input con id appointments_submit)
            submit_button = self.driver.find_element(By.ID, "appointments_submit")
            submit_button.click()
            time.sleep(1)


            #Dar click en el enlace (a) con la clase "button alert"
            #CUIDADO QUE ESCOGE CITA
            alert_button = self.driver.find_element(By.CSS_SELECTOR, "a.button.alert")
            alert_button.click()
            time.sleep(10)
            
            self.warning_controller(f"FECHA SELECCIONADA Y ENVIADA {month} el {day} en {self.location}")
            alert_system = EmailAlert()
            alert_system.send_email_alert("CITA AUTO PROGRAMADA! ", month, day, self.location)
            time.sleep(45)
            sys.exit()
        except Exception as e:
            self.error_controller(f"Error en autoSelectDate: {e}")