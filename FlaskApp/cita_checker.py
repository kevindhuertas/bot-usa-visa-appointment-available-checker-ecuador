import sys
import os
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
import json
import random
import shutil

class AppointmentCheck:
    def __init__(self, 
                email: str,
                password: str,
                allowed_location_to_save_appointment: List[str],
                months: List[str],
                stop_month: List[str],
                blocked_days: List[str],
                logger: logging.Logger,
                user_id: str,
                appoinment_id: str,
                country: str,
                ): #format: ["2025-03-27","2025-03-23"]
        self.user_id = user_id
        
        # Load country configuration
        self.country = country
        try:
            with open('countries.json', 'r') as f:
                countries_config = json.load(f)
            self.country_config = countries_config.get(self.country, {})
        except Exception as e:
            logger.error(f"Error cargando countries.json: {e}")
            self.country_config = {"code_link": "es-ec", "locations": ["Quito", "Guayaquil"]}
            
        self.code_link = self.country_config.get("code_link", "es-ec")
        self.country_locations = [loc.strip().lower() for loc in self.country_config.get("locations", [])]
        
        self.url = f"https://ais.usvisa-info.com/{self.code_link}/niv/schedule/{appoinment_id}/appointment"
        self.login_url = f"https://ais.usvisa-info.com/{self.code_link}/niv/users/sign_in"
        
        self.alert_sent = False
        self.location = ''
        self.pageLoadTime = 10
        
        # Filtrar locaciones permitidas para que estén en el país
        self.allowed_location_to_save_appointment = [
            loc for loc in allowed_location_to_save_appointment 
            if loc.strip().lower() in self.country_locations
        ]
        
        self.allowed_months_to_save_appointment = months
        self.stop_month = stop_month
        self.blocked_days = blocked_days
        self.email = email
        self.password = password
        self.logger = logger

        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Ejecuta el navegador en modo headless (sin interfaz gráfica)
        chrome_options.add_argument("--headless=new")  # headless recomendado
        chrome_options.add_argument("--disable-gpu")  # Necesario para algunos entornos headless
        chrome_options.add_argument("--no-sandbox")  # Evita errores en contenedores
        chrome_options.add_argument("--disable-dev-shm-usage")  # Mejora rendimiento en modo headless
        chrome_options.add_argument("--disable-extensions")  # Nueva opción para mejor rendimiento
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--enable-javascript")
        
        self.port = random.randint(10000, 60000)
        chrome_options.add_argument(f"--remote-debugging-port={self.port}")
        
        self.profile_dir = f"/tmp/chrome_profile_{self.port}_{self.user_id}"
        chrome_options.add_argument(f"--user-data-dir={self.profile_dir}")
        
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--window-size=1366,768")
        
        # driver_path = os.environ.get("CHROMEDRIVER_PATH")
        # if not driver_path:
        #     # fallback a ubicación habitual en Linux si chromedriver está instalado en el sistema
        #     driver_path = "/usr/bin/chromedriver"

        driver_path = os.environ.get("CHROMEDRIVER_PATH")
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
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")


    def check(self):
        try:
            self.driver.get(self.url)
            time.sleep(self.pageLoadTime)
            current_url = self.driver.current_url
            login_url = self.login_url

            if current_url == login_url:
                self.login()
                
                for attempt in range(10):
                    self.print_controller(f"Iniciando ciclo de chequeo {attempt + 1}/10")
                    
                    if attempt > 0:
                        self.driver.get(self.url)
                        time.sleep(self.pageLoadTime)

                    location_select_id = "appointments_consulate_appointment_facility_id"
                    checkbox_id = "confirmed_limit_message"
                    applicants_list_id = "applicants[]"
                    
                    # Esperamos a que ocurra ALGO relevante
                    try:
                        WebDriverWait(self.driver, self.pageLoadTime).until(
                            lambda d: (
                                d.current_url == login_url or
                                d.find_elements(By.ID, location_select_id) or
                                d.find_elements(By.ID, checkbox_id) or
                                d.find_elements(By.NAME, applicants_list_id)
                            )
                        )
                    except TimeoutException:
                        self.error_controller("No se pudo determinar el estado de la página")
                        break
                    
                    current_url_after = self.driver.current_url
                    if attempt == 0:
                        self.print_controller(f"Estado después del login: {current_url_after}")
                    
                    if current_url_after == login_url:
                        if attempt == 0:
                            self.error_controller("Fallo en el inicio de sesión, revisar credenciales")
                            return
                        else:
                            self.error_controller("La sesión expiró o redirigió a login inesperadamente.")
                            break
                            
                    # 1) Scheduling Limit
                    if self.driver.find_elements(By.ID, checkbox_id):
                        self.print_controller("Detectado checkbox 'confirmed_limit_message' (Scheduling Limit). Intentando aceptar...")
                        try:
                            checkbox = self.driver.find_element(By.ID, checkbox_id)
                            if not checkbox.is_selected():
                                self.driver.execute_script("arguments[0].click();", checkbox)
                            time.sleep(2)
                            submit_btn = self.driver.find_element(By.XPATH, "//input[@type='submit' and @name='commit']")
                            self.driver.execute_script("arguments[0].click();", submit_btn)

                            WebDriverWait(self.driver, self.pageLoadTime).until(
                                lambda d: (
                                    d.find_elements(By.ID, location_select_id) or 
                                    d.find_elements(By.NAME, applicants_list_id)
                                )
                            )
                            self.print_controller("Aceptado Scheduling Limit page")
                        except TimeoutException:
                            self.error_controller("No se pudo continuar desde Scheduling Limit (falló al marcar/submit).")
                            break

                    # 2) Applicants List
                    if self.driver.find_elements(By.NAME, applicants_list_id):
                        self.print_controller("Detectada página 'Applicants List'. Intentando aceptar...")
                        try:
                            applicants_checkboxes = self.driver.find_elements(By.NAME, applicants_list_id)
                            
                            cantidad_aplicantes = len(applicants_checkboxes)
                            self.print_controller(f"Cantidad de aplicantes encontrados: {cantidad_aplicantes}")
                            if cantidad_aplicantes > 0:
                                texto_completo = applicants_checkboxes[0].find_element(By.XPATH, "./../..").text.strip()
                                nombres_aplicantes = [nombre.strip() for nombre in texto_completo.split('\n') if nombre.strip()]
                                self.print_controller(f"Lista de aplicantes: {nombres_aplicantes}")
                            
                            for checkbox in applicants_checkboxes:
                                if not checkbox.is_selected():
                                    self.driver.execute_script("arguments[0].click();", checkbox)
                                    
                            time.sleep(2)
                            submit_btn = self.driver.find_element(By.XPATH, "//input[@type='submit' and @name='commit']")
                            self.driver.execute_script("arguments[0].click();", submit_btn)

                            WebDriverWait(self.driver, self.pageLoadTime).until(
                                EC.presence_of_element_located((By.ID, location_select_id))
                            )
                            self.print_controller("Aceptada Applicants List page")
                        except TimeoutException:
                            self.error_controller("No se pudo continuar desde la lista de aplicantes.")
                            break

                    # 3) Verificación final: confirmar que el ID de reprogramación existe
                    if self.driver.find_elements(By.ID, location_select_id):
                        if attempt == 0:
                            self.print_controller("Página de reprogramación detectada correctamente")
                            self.client_print_controller("Proceso encontrado")
                            self.client_print_controller("Se inicio sesion correctamente")
                            
                        # Here we check dates
                        current_url_after_process = self.driver.current_url
                        # self.print_controller("Url actual: " + current_url_after_process)
                        if self.url in current_url_after_process:
                            self.check_dates()
                        else:
                            self.error_controller("Hubo fallo al encontrar pagina de reprogramacion")
                    else:
                        self.error_controller("No se encontró la página de reprogramación: revisar si el ID DE PROCESO es correcto")
                        break
                        
                    if attempt < 9:
                        wait_time = random.randint(20, 40)
                        self.print_controller(f"Esperando {wait_time} segundos antes del siguiente chequeo...")
                        time.sleep(wait_time)
            else:
                self.error_controller("El programa no responde a la pagina de citas. Url actual: " + current_url)
        except Exception as e:
            self.error_controller(f"Error durante el proceso de inicio de sesión y redirección a verificación de citas: {e}")
        finally:
            self.driver.quit()
            # Clean up the custom profile directory
            try:
                if os.path.exists(self.profile_dir):
                    shutil.rmtree(self.profile_dir, ignore_errors=True)
            except Exception as e:
                self.error_controller(f"Error limpiando directorio de perfil: {e}")

    def error_controller(self, e):
        self.logger.error(f"Error: {e}")

    def print_controller(self, e):
        self.logger.info(f"{e}")

    def client_print_controller(self, e):
        self.logger.info(f"CLIENT: {e}")

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
            self.print_controller("Intentando iniciar sesión haciendo click en ingresar...")
        except Exception as e:
            self.error_controller(f"Error durante el proceso de inicio de sesión: {e}")

    def check_dates(self):
        try:
            self.print_controller("Continuando con checkeo en página de citas")
            self.client_print_controller("Monitoreo en curso...")
            location_select_id = "appointments_consulate_appointment_facility_id"
            date_input_id = "appointments_consulate_appointment_date"
            first_group_class = "ui-datepicker-group-first"
            next_button_class = "ui-datepicker-next"

            for loc in self.allowed_location_to_save_appointment:
                self.location = loc.strip()
                self.print_controller(f"Verificando citas para la locación: {self.location}")
                
                location_select = WebDriverWait(self.driver, self.pageLoadTime).until(
                    EC.presence_of_element_located((By.ID, location_select_id))
                )
                location_select.click()
                time.sleep(1)

                options = location_select.find_elements(By.TAG_NAME, "option")
                option_found = False
                for option in options:
                    if option.text.strip().lower() == self.location.lower():
                        option.click()
                        option_found = True
                        break

                if not option_found:
                    self.print_controller(f"La locación {self.location} no se encontró en las opciones, se omite.")
                    self.driver.find_element(By.TAG_NAME, "body").click()
                    continue

                time.sleep(1)
                self.verify_dates_until_june(date_input_id, first_group_class, next_button_class)

                self.alert_sent = False
                self.driver.find_element(By.TAG_NAME, "body").click()
                time.sleep(0.2)
                try:
                    self.driver.find_element(By.ID, "header").click()
                    time.sleep(0.2)
                except:
                    pass

        except Exception as e:
            self.error_controller(f"Error durante la verificación de fechas de citas: {e}")

    def verify_dates_until_june(self, date_input_id, first_group_class, next_button_class):
        month_count = 0
        max_months = 3
        while month_count < max_months:
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
                month_count += 1
                time.sleep(2)
            except Exception as e:
                self.error_controller(f"Error durante la verificación diaria de fechas de citas")
                break

    def check_calendar_group(self, group_class):
        try:
            calendar_group = self.driver.find_element(By.CLASS_NAME, group_class)
            month_element = calendar_group.find_element(By.CLASS_NAME, "ui-datepicker-month")
            month = month_element.text.strip().lower()
            tbody = calendar_group.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
            month_map = {
                'enero': '01','january': '01', 'febrero': '02', 'february': '02',
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
                            allowed_month_numbers = [month_map[m.lower()] for m in self.allowed_months_to_save_appointment if m.lower() in month_map]
                            
                            is_blocked = any(
                                blocked_date.endswith(current_date)
                                for blocked_date in self.blocked_days
                            )

                            self.print_controller(f"Fecha disponible detectada: {month} {day_number} en {self.location} {'(BLOQUEADA)' if is_blocked else ''}")
                            
                            if current_month in allowed_month_numbers:
                                if self.location.lower() in [l.lower() for l in self.allowed_location_to_save_appointment]:
                                    if not is_blocked:
                                        self.client_print_controller(f"Cita valida encontrada en {self.location} para {current_date}")
                                        self.alert_available_date(month, day_number)
                                        a_tag[0].click()
                                        self.warning_controller(f"AUTOPROGRAMACION en {self.location} el: {current_date}")
                                        self.auto_select_date(month, day_number)
                                    else:
                                        self.warning_controller(f"Fecha bloqueada detectada, cita encontrada el: {current_date}")
                                else:
                                    self.warning_controller(f"Fecha fuera de locacion permitida, cita encontrada el: {current_date} en {self.location} ")
                            else:
                                self.warning_controller(f"Fecha fuera de mes permitido, cita encontrada el: {current_date} en {self.location}")
        except Exception as e:
            self.error_controller(f"Error durante la verificación del grupo de calendario")

    def alert_available_date(self, month, day):
        if (self.alert_sent== False):
            alert_system = EmailAlert()
            alert_system.send_email_alert("CITA DISPONIBLE:", month, day, self.location)
            self.warning_controller(f"ALERTA A EMAIL: Fecha disponible el {day} de {month} en {self.location}")
            self.alert_sent = True

    def auto_select_date(self, month, day):
        # self.print_controller("MODO PRUEBA auto_select_date la fecha {month} {day} en {self.location} ");
        # sys.exit();
        # return
    
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
            time.sleep(0.5)


            #Dar click en el enlace (a) con la clase "button alert"
            #CUIDADO QUE ESCOGE CITA
            alert_button = self.driver.find_element(By.CSS_SELECTOR, "a.button.alert")
            alert_button.click()
            time.sleep(10)
            
            self.client_print_controller(f"Cita programada con exito en {self.location} para {month} {day}")
            self.warning_controller(f"FECHA SELECCIONADA Y ENVIADA {month} el {day} en {self.location}")
            alert_system = EmailAlert()
            alert_system.send_email_alert("CITA AUTO PROGRAMADA! ", month, day, self.location)
            time.sleep(45)
            sys.exit()
        except Exception as e:
            self.error_controller(f"Error en autoSelectDate: {e}")