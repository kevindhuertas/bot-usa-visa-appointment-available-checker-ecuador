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
try:
    from supabase_client import create_record, read_records, update_record, delete_record
except Exception:
    create_record = None
    read_records = None
    update_record = None
    delete_record = None
import json
import random
import shutil

class AppointmentCheckColombia:
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
                user_email_alert: str,
                auto_programacion_allowed: bool,
                nearest_cas_appointment: bool,
                # allowed_sas_days:List[str],
                current_consular_appointment_date: str
                # fecha_cita_actual: str,Error durante la verificación diaria 
                # fecha_cas_permitida: List[str]
                ): #format: ["2025-03-27","2025-03-23"]
        self.user_id = user_id
        # Guardar el id del appointment para referenciar procesos en DB
        self.appointment_id = appoinment_id
        self.country = country
        # Email donde se enviarán las alertas además del email principal
        self.user_email_alert = user_email_alert
        try:
            with open('countries.json', 'r') as f:
                countries_config = json.load(f)
            self.country_config = countries_config.get(self.country, {})
        except Exception as e:
            logger.error(f"Error cargando countries.json: {e}")
            self.country_config = {"code_link": "es-ec", "locations": ["Quito", "Guayaquil"]}
            
        self.code_link = self.country_config.get("code_link", "es-ec")
        self.country_locations = [loc.strip().lower() for loc in self.country_config.get("locations", [])]
        
        self.url = f"https://ais.usvisa-info.com/{self.code_link}/niv/schedule/{self.appointment_id}/appointment"
        self.login_url = f"https://ais.usvisa-info.com/{self.code_link}/niv/users/sign_in"
        
        self.alert_sent = False
        self.location = ''
        self.pageLoadTime = 10

        # API config
        self.check_interval_min = 75
        self.check_interval_max = 100
        self.max_check_attempts = 5
        self.max_months = 4
        
        self.allowed_location_to_save_appointment = [
            loc for loc in allowed_location_to_save_appointment 
            if loc.strip().lower() in self.country_locations
        ]
        self.allowed_months_to_save_appointment = months
        self.auto_programacion_allowed = auto_programacion_allowed
        self.stop_month = stop_month
        self.blocked_days = blocked_days
        self.blocked_days_reset = blocked_days
        self.nearest_cas_appointment = nearest_cas_appointment
        # self.allowed_sas_days = allowed_sas_days
        self.current_consular_appointment_date = current_consular_appointment_date
        self.consular_appointment_date_confirmed = None
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

       # Obtener el path del entorno (Docker/Cloud Run)
        driver_path = os.environ.get("CHROMEDRIVER_PATH")
        if not driver_path:
            if platform.system() == "Windows":
                driver_path = "./drivers/chromedriver.exe"
            elif platform.system() == "Darwin":
                driver_path = "./drivers/chromedriver" # Tu Mac usará este
            elif platform.system() == "Linux":
                driver_path = "./drivers/chromedriverlinux"
            else:
                raise Exception("Sistema operativo no soportado.")
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def check(self):
        try:
            # Al iniciar el proceso reseteamos el historial de errores en la DB
            try:
                self._reset_process_error_history()
            except Exception:
                # No queremos que falle el inicio por errores de DB
                pass
            self.driver.get(self.url)
            time.sleep(self.pageLoadTime)
            current_url = self.driver.current_url
            login_url = self.login_url

            if current_url == login_url:
                self.login()
                
                for attempt in range(self.max_check_attempts):
                    self.print_controller(f"Ciclo de chequeo {attempt + 1}/{self.max_check_attempts}")
                    
                    if attempt > 0:
                        self.driver.get(self.url)
                        time.sleep(self.pageLoadTime)

                    location_select_id = "appointments_consulate_appointment_facility_id"
                    checkbox_id = "confirmed_limit_message"
                    applicants_list_id = "applicants[]"
                    
                    iteration_failed = False

                    # Esperamos a que ocurra ALGO relevante
                    try:
                        WebDriverWait(self.driver, self.pageLoadTime).until(
                            lambda d: (
                                d.find_elements(By.ID, location_select_id) or
                                d.find_elements(By.ID, checkbox_id) or
                                d.find_elements(By.NAME, applicants_list_id)
                            )
                        )
                    except TimeoutException:
                        current_url_after = self.driver.current_url
                        if attempt == 0:
                            self.print_controller(f"Estado después del login: {current_url_after}")

                        if login_url in current_url_after:
                            if attempt == 0:
                                self.error_controller("Fallo en el inicio de sesión, revisar credenciales")
                                return
                            else:
                                self.error_controller("La sesión expiró o redirigió a login inesperadamente.")
                                iteration_failed = True
                        else:
                            self.error_controller("No se pudo determinar el estado de la página")
                            iteration_failed = True

                    if not iteration_failed:
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
                                iteration_failed = True

                    if not iteration_failed:
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
                                iteration_failed = True

                    if not iteration_failed:
                        # 3) Verificación final: confirmar que el ID de reprogramación existe
                        if self.driver.find_elements(By.ID, location_select_id):
                            if attempt == 0:
                                self.print_controller("Página de reprogramación detectada correctamente")
                                self.client_print_controller("Se inicio sesion correctamente & Proceso encontrado")
                                
                            # Here we check dates
                            current_url_after_process = self.driver.current_url
                            # self.print_controller("Url actual: " + current_url_after_process)
                            if self.url in current_url_after_process:
                                self.check_dates()
                            else:
                                self.error_controller("Hubo fallo al encontrar pagina de reprogramacion")
                                iteration_failed = True
                        else:
                            self.error_controller("No se encontró la página de reprogramación: revisar si el ID DE PROCESO es correcto")
                            iteration_failed = True
                            
                    if attempt < self.max_check_attempts:
                        wait_time = random.randint(self.check_interval_min, self.check_interval_max)
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
        # Guardar historial de errores en el proceso (no bloquear en caso de fallo)
        try:
            self._append_process_error(str(e))
        except Exception:
            pass

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
            location_select_id = "appointments_consulate_appointment_facility_id"
            date_input_id = "appointments_consulate_appointment_date"
            first_group_class = "ui-datepicker-group-first"
            next_button_class = "ui-datepicker-next"
            
            for loc in self.allowed_location_to_save_appointment:
                self.location = loc.strip()
                self.client_print_controller(f"Verificando citas para la locación: {self.location}")
                
                location_select = WebDriverWait(self.driver, self.pageLoadTime).until(
                    EC.presence_of_element_located((By.ID, location_select_id))
                )
                location_select.click()
                time.sleep(1)

                options = location_select.find_elements(By.TAG_NAME, "option")
                option_found = False
                for option in options:
                    if option.text.strip().lower() == self.location.lower():
                        self.client_print_controller("Monitoreo en curso en la locación: " + self.location.lower())
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
        self.client_print_controller("Verificando fechas disponibles hasta el mes de " + ", ".join(self.allowed_months_to_save_appointment))
        while month_count < self.max_months:
            try:
                 #Verificar que si este abierto el date picker
                self.open_datepicker(date_input_id)
                self.check_calendar_group(first_group_class,date_input_id)
                if self.alert_sent: break
                #Verificar que si este abierto el date picker
                self.open_datepicker(date_input_id)


                first_group = self.driver.find_element(By.CLASS_NAME, first_group_class)
                current_month = first_group.find_element(By.CLASS_NAME, "ui-datepicker-month").text
                self.print_controller(f"Vericando mes consular: {current_month}")
                if current_month.lower() in [m.lower() for m in self.stop_month]:
                    self.print_controller(f"Mes de {current_month} alcanzado, terminando la verificación.")
                    break
                
                # Pasar al siguiente mes (doble clic en el botón "next" para asegurarnos de avanzar mes a mes)
                next_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, next_button_class)))
                self.driver.execute_script("arguments[0].click();", next_button)
                month_count += 1
                time.sleep(2)
            except Exception as e:
                self.error_controller(f"Error durante la verificación diaria de fechas de citas {e}")
                break

    def open_datepicker(self, date_input_id):
        try:
            date_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, date_input_id))
            )
            self.driver.execute_script("arguments[0].click();", date_input)
            return True
        except TimeoutException:
            self.error_controller("No se pudo abrir el datepicker a tiempo.")
            return False
        except Exception as e:
            self.error_controller(f"Error al abrir el datepicker: {e}")
            return False
        
    def check_calendar_group(self, group_class, date_input_id):
        # Envolvemos todo en un while para poder "reiniciar" la búsqueda fácilmente
        while True:
            try:
                # 1. Obtenemos elementos FRESCOS cada vez que el ciclo while se reinicia
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

                # Bandera para saber si necesitamos reiniciar el escaneo desde cero
                necesita_reiniciar = False

                for row in rows:
                    days = row.find_elements(By.TAG_NAME, "td")
                    for day in days:
                        if "ui-datepicker-unselectable" not in day.get_attribute("class"):
                            a_tag = day.find_elements(By.TAG_NAME, "a")
                            if a_tag:
                                day_number = a_tag[0].text.zfill(2)
                                current_month = month_map.get(month, '00')
                                current_date = f"{current_month}-{day_number}"
                                allowed_month_numbers = [month_map[m.lower()] for m in self.allowed_months_to_save_appointment if m.lower() in month_map]
                                
                                is_blocked = any(blocked_date.endswith(current_date) for blocked_date in self.blocked_days)

                                self.print_controller(f"Fecha disponible detectada: {month} {day_number} en {self.location} {'(BLOQUEADA)' if is_blocked else ''}")
                                
                                if current_month in allowed_month_numbers:
                                    if self.location.lower() in [l.lower() for l in self.allowed_location_to_save_appointment]:
                                        if not is_blocked:
                                            self.client_print_controller(f"Cita Consular valida encontrada en {self.location} para {current_date}")
                                            a_tag[0].click()
                                            self.consular_appointment_date_confirmed = f"{current_month}-{day_number}"
                                            selectSubmit = self.auto_select_date(month, day_number)
                                            
                                            if not selectSubmit:
                                                self.print_controller(f"No se pudo subir la cita para la fecha: {current_date}, intentando con la siguiente.")
                                                
                                                # Agregamos a la lista negra
                                                if current_date not in self.blocked_days:
                                                    self.blocked_days.append(current_date)
                                                
                                                # Reabrimos el calendario
                                                self.open_datepicker(date_input_id)
                                                
                                                # Activamos la bandera y rompemos el bucle 'for day in days'
                                                necesita_reiniciar = True
                                                break 

                                        else:
                                            self.warning_controller(f"Fecha bloqueada detectada, cita encontrada el: {current_date}")
                                    else:
                                        self.warning_controller(f"Fecha fuera de locacion permitida, cita encontrada el: {current_date} en {self.location} ")
                                else:
                                    self.warning_controller(f"Fecha fuera de mes permitido, cita encontrada el: {current_date} en {self.location}")

                    # Si la bandera se activó en el bucle de días, rompemos también el bucle de filas ('for row in rows')
                    if necesita_reiniciar:
                        break

                # Si llegamos aquí y necesita_reiniciar es True, el 'continue' nos manda de vuelta al inicio del 'while True'
                # Esto vuelve a buscar los elementos (calendar_group, rows, etc.) desde cero.
                if necesita_reiniciar:
                    continue
                
                # Si llegamos aquí y necesita_reiniciar es False, significa que revisamos todo el mes exitosamente.
                # Rompemos el while True para terminar la función.
                break

            except Exception as e:
                self.error_controller(f"Error durante la verificación del grupo de calendario {e}")
                break # Rompemos el while para evitar un bucle infinito en caso de error grave

    def alert_available_date(self, month, day):
        if (self.alert_sent== False):
            recipients = self.user_email_alert if self.user_email_alert else ""
            alert_system = EmailAlert(recipients)
            alert_system.send_email_alert(f"CITA DISPONIBLE para {self.email}:", month, day, self.location, user_id=self.user_id)
            self.warning_controller(f"ALERTA A EMAIL: Fecha disponible el {day} de {month} en {self.location}")
            self.alert_sent = True

    def auto_select_option(self, select_element):
        try:
            time.sleep(3)
            select_element.click()
            time.sleep(2)
            options = select_element.find_elements(By.TAG_NAME, "option")
            time.sleep(1)
            # Verificar que exista al menos una segunda opción
            if len(options) < 2:
                self.print_controller("No hay suficientes opciones disponibles en el select para seleccionar una cita.")
                time.sleep(3)
                select_element = self.driver.find_element(By.ID, "appointments_consulate_appointment_time")
                select_element.click()
                time.sleep(8)
                # Obtener todas las opciones disponibles dentro del select
                options = select_element.find_elements(By.TAG_NAME, "option")
                time.sleep(1)
                if len(options) < 2:
                    return
            options[1].click()
        except Exception as e:
            self.error_controller(f"Error en auto_select_option: {e}")

    def _select_option_by_location(self, select_element):
        try:
            select_element.click()
            time.sleep(0.5)
            options = select_element.find_elements(By.TAG_NAME, "option")
            if not options:
                return
            desired_option = None
            for option in options:
                if self.location.lower() in option.text.strip().lower():
                    desired_option = option
                    break
            if desired_option is None and len(options) > 1:
                desired_option = options[1]
            if desired_option and not desired_option.is_selected():
                self.driver.execute_script("arguments[0].click();", desired_option)
            time.sleep(0.5)
        except Exception as e:
            self.error_controller(f"Error seleccionando opción por ubicación en CAS: {e}")


    def _explore_all_cas_dates(self, date_input_id, group_class, next_button_class):
        """
        FASE 1: Abre el calendario y escanea todas las fechas disponibles hasta 
        encontrar la fecha consular o agotar los meses. No hace clic en las fechas, solo las recolecta.
        """
        available_dates = []
        try:
            time.sleep(1)
            date_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, date_input_id))
            )
            self.client_print_controller("Explorando todas las fechas disponibles en CAS...")

            self.driver.execute_script("arguments[0].click();", date_input)
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, group_class))
            )

            month_map = {
                'enero': '01','january': '01', 'febrero': '02', 'february': '02',
                'marzo': '03', 'march': '03', 'abril': '04', 'april': '04',
                'mayo': '05', 'may': '05', 'junio': '06', 'june': '06',
                'julio': '07', 'july': '07', 'agosto': '08', 'august': '08',
                'septiembre': '09', 'september': '09', 'octubre': '10',
                'october': '10', 'noviembre': '11', 'november': '11',
                'diciembre': '12', 'december': '12'
            }

            consular_date = getattr(self, 'consular_appointment_date_confirmed', None)
            stop_exploration = False

            for _ in range(self.max_months):
                calendar_groups = self.driver.find_elements(By.CLASS_NAME, group_class)
                for group in calendar_groups:
                    try:
                        month_text = group.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
                    except Exception:
                        continue

                    tbody = group.find_element(By.TAG_NAME, "tbody")
                    days = tbody.find_elements(By.TAG_NAME, "td")
                    
                    for day in days:
                        if "ui-datepicker-unselectable" in day.get_attribute("class"):
                            continue
                        a_tags = day.find_elements(By.TAG_NAME, "a")
                        if not a_tags:
                            continue
                        
                        day_number = a_tags[0].text.zfill(2)
                        month_number = month_map.get(month_text, '00')
                        date_identifier = f"{month_number}-{day_number}"
                        
                        # Si llegamos a la fecha consular, marcamos bandera para detener todo
                        if consular_date and date_identifier == consular_date:
                            self.print_controller(f"Se alcanzó la fecha Consular ({consular_date}). Fin del mapeo.")
                            stop_exploration = True
                            break 

                        if date_identifier not in available_dates:
                            available_dates.append(date_identifier)

                    if stop_exploration:
                        break

                if stop_exploration:
                    break
                    
                # Pasar al siguiente mes
                next_buttons = self.driver.find_elements(By.CLASS_NAME, next_button_class)
                if not next_buttons:
                    break
                self.driver.execute_script("arguments[0].click();", next_buttons[0])
                time.sleep(0.5)

            # Terminó la exploración. Cerramos el calendario haciendo clic fuera
            try:
                self.driver.find_element(By.TAG_NAME, "body").click()
                time.sleep(1)
            except:
                pass

        except TimeoutException:
            if "El sistema está ocupado" in self.driver.page_source:
                self.client_print_controller("El sistema está ocupado al intentar explorar el calendario CAS.")
            else:
                self.error_controller("No se pudo abrir el datepicker de CAS para explorar.")
        except Exception as e:
            self.error_controller(f"Error explorando fechas CAS: {e}")
            
        return available_dates

    def _click_specific_cas_date(self, target_date, date_input_id, group_class, next_button_class):
        """
        FASE 2A: Abre el calendario y busca secuencialmente una fecha en específico.
        Como el calendario se reinicia al cerrarse, navega mes por mes hasta encontrarla y le da clic.
        """
        try:
            date_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, date_input_id))
            )
            self.driver.execute_script("arguments[0].click();", date_input)
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, group_class))
            )

            month_map = {
                'enero': '01','january': '01', 'febrero': '02', 'february': '02',
                'marzo': '03', 'march': '03', 'abril': '04', 'april': '04',
                'mayo': '05', 'may': '05', 'junio': '06', 'june': '06',
                'julio': '07', 'july': '07', 'agosto': '08', 'august': '08',
                'septiembre': '09', 'september': '09', 'octubre': '10',
                'october': '10', 'noviembre': '11', 'november': '11',
                'diciembre': '12', 'december': '12'
            }

            target_month, target_day = target_date.split('-')

            for _ in range(self.max_months):
                calendar_groups = self.driver.find_elements(By.CLASS_NAME, group_class)
                for group in calendar_groups:
                    try:
                        month_text = group.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
                    except Exception:
                        continue

                    current_month_number = month_map.get(month_text, '00')
                    
                    # Si encontramos el mes objetivo, buscamos el día
                    if current_month_number == target_month:
                        tbody = group.find_element(By.TAG_NAME, "tbody")
                        days = tbody.find_elements(By.TAG_NAME, "td")
                        for day in days:
                            a_tags = day.find_elements(By.TAG_NAME, "a")
                            if a_tags and a_tags[0].text.zfill(2) == target_day:
                                a_tags[0].click() # El calendario se cierra al hacer clic
                                time.sleep(1)
                                return True

                # Si no es el mes objetivo, pasamos de mes
                next_buttons = self.driver.find_elements(By.CLASS_NAME, next_button_class)
                if not next_buttons:
                    break
                self.driver.execute_script("arguments[0].click();", next_buttons[0])
                time.sleep(0.5)

            return False
        except Exception as e:
            self.warning_controller(f"Error intentando buscar la fecha específica {target_date}: {e}")
            return False

    def _select_cas_time_if_available(self):
        # Esta función se mantiene igual, no necesita cambios.
        select_id = "appointments_asc_appointment_time"
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, select_id))
            )

            def _retrieve_options(driver):
                options = driver.find_element(By.ID, select_id).find_elements(By.TAG_NAME, "option")
                return options if options else False

            options = WebDriverWait(self.driver, 10).until(_retrieve_options)
            if len(options) < 2:
                return False

            select_element = self.driver.find_element(By.ID, select_id)
            self.driver.execute_script("arguments[0].click();", select_element)
            time.sleep(2)
            options = select_element.find_elements(By.TAG_NAME, "option")
            if len(options) < 2:
                return False
            self.driver.execute_script("arguments[0].click();", options[1])
            time.sleep(0.5)
            return True
        except TimeoutException:
            if "El sistema está ocupado" in self.driver.page_source:
                self.warning_controller("El sistema está ocupado al cargar horarios CAS. Se marcará como fallida y se probará otra fecha.")
            else:
                self.warning_controller("Timeout esperando el select de horario CAS.")
            return False
        except Exception as e:
            self.error_controller(f"Error seleccionando horario CAS: {e}")
            return False

    def CheckCASDateColombia(self):
        try:
            time.sleep(3)
            if self.location.strip().lower() != "bogota":
                return True

            date_input_id = "appointments_asc_appointment_date"
            first_group_class = "ui-datepicker-group-first"
            next_button_class = "ui-datepicker-next"

            # 1. EXPLORAR Y RECOLECTAR
            available_dates = self._explore_all_cas_dates(date_input_id, first_group_class, next_button_class)

            if not available_dates:
                self.warning_controller("No se encontraron fechas disponibles para CAS previas a la cita Consular.")
                return False

            self.client_print_controller(f"Total de fechas CAS disponibles: {available_dates}")

            # 2. DEFINIR ESTRATEGIA (Ordenamiento)
            # Como la exploración añade las fechas en orden cronológico real,
            # solo necesitamos invertir la lista si queremos la más cercana a la consular (las últimas).
            is_nearest = getattr(self, 'nearest_cas_appointment', False)
            if is_nearest:
                available_dates.reverse() # Invertimos para empezar por las fechas más tardías
                self.client_print_controller("CAS: Buscar la fecha CAS más cercana a la cita Consular.")
            else:
                self.client_print_controller("CAS: Buscar la fecha CAS más alejada (lo más pronto posible).")
            # 3. ITERAR SOBRE LAS FECHAS OBJETIVO
            for target_date in available_dates:
                self.client_print_controller(f"Revisando disponibilidad de horario para la fecha: {target_date}...")
                
                # Vamos directamente a buscar esa fecha abriendo el calendario desde cero
                clicked = self._click_specific_cas_date(target_date, date_input_id, first_group_class, next_button_class)
               
                if clicked:
                    # La fecha fue clickeada (el calendario se cerró), revisamos si hay hora
                    if self._select_cas_time_if_available():
                        self.client_print_controller(f"¡Éxito! Horario CAS seleccionado para la fecha {target_date}.")
                        self.driver.find_element(By.TAG_NAME, "body").click()
                        return True
                    else:
                        
                        self.warning_controller(f"Sin horario en {target_date}. Intentando la siguiente de la lista...")
                        time.sleep(1) # Pausa requerida antes de reabrir el calendario
                else:
                    self.warning_controller(f"Fallo técnico al intentar seleccionar {target_date}. Saltando...")
                    time.sleep(1)

            self.warning_controller("Se revisaron todas las fechas mapeadas y ninguna tenía horarios disponibles.")
            return False
            
        except Exception as e:
            self.error_controller(f"Error general durante la verificación de fechas CAS: {e}")
            return False

    def auto_select_date(self, month, day):
        try:
            time_select = self.driver.find_element(By.ID, "appointments_consulate_appointment_time")
            self.auto_select_option(time_select)
            self.driver.find_element(By.TAG_NAME, "body").click()
            cas_ready = self.CheckCASDateColombia()
            
            if not cas_ready:
                self.warning_controller("Se detiene el proceso de auto programación por falta de horarios CAS disponibles válidos.")
                return False
                
            self.auto_submit_reprogramacion_cita(month, day)
            return True
            
        except Exception as e:
            self.error_controller(f"Error en auto_select_date: {e}")
            return False
            
    # def _select_next_available_cas_date(self, date_input_id, group_class, next_button_class, visited_dates):
    #     try:
    #         time.sleep(1)

    #         date_input = WebDriverWait(self.driver, 10).until(
    #             EC.presence_of_element_located((By.ID, date_input_id))
    #         )
    #         self.client_print_controller("Revisando fechas disponibles en CAS...")

    #         self.driver.execute_script("arguments[0].click();", date_input)
    #         WebDriverWait(self.driver, 10).until(
    #             EC.visibility_of_element_located((By.CLASS_NAME, group_class))
    #         )

    #         month_map = {
    #             'enero': '01','january': '01', 'febrero': '02', 'february': '02',
    #             'marzo': '03', 'march': '03', 'abril': '04', 'april': '04',
    #             'mayo': '05', 'may': '05', 'junio': '06', 'june': '06',
    #             'julio': '07', 'july': '07', 'agosto': '08', 'august': '08',
    #             'septiembre': '09', 'september': '09', 'octubre': '10',
    #             'october': '10', 'noviembre': '11', 'november': '11',
    #             'diciembre': '12', 'december': '12'
    #         }

    #         max_months = 3
    #         for _ in range(max_months):
    #             calendar_groups = self.driver.find_elements(By.CLASS_NAME, group_class)
    #             for group in calendar_groups:
    #                 try:
    #                     month_text = group.find_element(By.CLASS_NAME, "ui-datepicker-month").text.strip().lower()
    #                 except Exception:
    #                     continue

    #                 tbody = group.find_element(By.TAG_NAME, "tbody")
    #                 days = tbody.find_elements(By.TAG_NAME, "td")
    #                 for day in days:
    #                     if "ui-datepicker-unselectable" in day.get_attribute("class"):
    #                         continue
    #                     a_tags = day.find_elements(By.TAG_NAME, "a")
    #                     if not a_tags:
    #                         continue
                        
    #                     day_number = a_tags[0].text.zfill(2)
    #                     month_number = month_map.get(month_text, '00')
    #                     date_identifier = f"{month_number}-{day_number}"
                        
    #                     # --- NUEVO: FRENO DE EMERGENCIA CONSULAR ---
    #                     # Si llegamos a la fecha confirmada de la cita consular, detenemos todo.
    #                     # Usamos getattr por seguridad, por si la variable llega vacía o no existe aún.
    #                     consular_date = self.consular_appointment_date_confirmed
    #                     if consular_date and date_identifier == consular_date:
    #                         self.warning_controller(f"Límite alcanzado: El calendario CAS llegó a la fecha de la cita Consular ({date_identifier}). Se aborta la búsqueda.")
    #                         return "ABORT" # Enviamos una señal de aborto al bucle principal

    #                     # 1. Verificamos si ya revisamos esta fecha
    #                     if date_identifier in visited_dates:
    #                         continue

    #                     # 2. Validación con self.allowed_sas_days
    #                     if getattr(self, 'allowed_sas_days', []): 
    #                         is_allowed = any(
    #                             allowed_date.endswith(date_identifier) for allowed_date in self.allowed_sas_days
    #                         )
    #                         if not is_allowed:
    #                             continue 

    #                     # 3. Guardamos la fecha en visitadas ANTES de hacer click
    #                     visited_dates.add(date_identifier)
                        
    #                     try:
    #                         a_tags[0].click()
    #                         time.sleep(1)
    #                         return date_identifier
    #                     except Exception as e:
    #                         self.warning_controller(f"Error al hacer clic en la fecha {date_identifier}: {e}. Intentando la siguiente...")
    #                         continue 

    #             next_buttons = self.driver.find_elements(By.CLASS_NAME, next_button_class)
    #             if not next_buttons:
    #                 break
    #             self.driver.execute_script("arguments[0].click();", next_buttons[0])
    #             time.sleep(1)

    #     except TimeoutException:
    #         page_source = self.driver.page_source
    #         if "El sistema está ocupado" in page_source:
    #             self.client_print_controller("El sistema está ocupado al intentar abrir el calendario CAS.")
    #         else:
    #             self.error_controller("No se pudo abrir el datepicker de CAS a tiempo.")
    #     except Exception as e:
    #         self.error_controller(f"Error seleccionando la siguiente fecha disponible para CAS: {e}")
    #     return None

    # def _select_cas_time_if_available(self):
    #     select_id = "appointments_asc_appointment_time"
    #     try:
    #         WebDriverWait(self.driver, 10).until(
    #             EC.presence_of_element_located((By.ID, select_id))
    #         )

    #         def _retrieve_options(driver):
    #             options = driver.find_element(By.ID, select_id).find_elements(By.TAG_NAME, "option")
    #             return options if options else False

    #         options = WebDriverWait(self.driver, 10).until(_retrieve_options)
    #         if len(options) < 2:
    #             self.print_controller("No hay horarios CAS disponibles para la fecha seleccionada.")
    #             return False

    #         select_element = self.driver.find_element(By.ID, select_id)
    #         self.driver.execute_script("arguments[0].click();", select_element)
    #         time.sleep(2)
    #         options = select_element.find_elements(By.TAG_NAME, "option")
    #         if len(options) < 2:
    #             self.print_controller("No hay horarios CAS disponibles tras refrescar opciones.")
    #             return False
    #         self.driver.execute_script("arguments[0].click();", options[1])
    #         time.sleep(0.5)
    #         return True
    #     except TimeoutException:
    #         if "El sistema está ocupado" in self.driver.page_source:
    #             self.warning_controller("El sistema está ocupado al cargar horarios CAS. Se marcará como fallida y se probará otra fecha.")
    #         else:
    #             self.warning_controller("Timeout esperando el select de horario CAS.")
    #         return False
    #     except Exception as e:
    #         self.error_controller(f"Error seleccionando horario CAS: {e}")
    #         return False

    # def CheckCASDateColombia(self):
    #     try:
    #         time.sleep(1)
    #         if self.location.strip().lower() != "bogota":
    #             return True

    #         date_input_id = "appointments_asc_appointment_date"
    #         first_group_class = "ui-datepicker-group-first"
    #         next_button_class = "ui-datepicker-next"

    #         visited_dates = set()
    #         # --- NUEVO: Se aumentó el límite a 8 ---
    #         max_dates_to_check = 8 
    #         checked_dates = 0

    #         while checked_dates < max_dates_to_check:
    #             selected_date = self._select_next_available_cas_date(
    #                 date_input_id,
    #                 first_group_class,
    #                 next_button_class,
    #                 visited_dates
    #             )

    #             # --- NUEVO: Recibimos la señal de aborto ---
    #             if selected_date == "ABORT":
    #                 self.print_controller("Proceso CAS cancelado definitivamente por coincidencia con cita Consular.")
    #                 return False

    #             if not selected_date:
    #                 self.print_controller("No hay más fechas disponibles en el calendario CAS o no cumplen el filtro.")
    #                 break

    #             if self._select_cas_time_if_available():
    #                 self.client_print_controller(f"Horario CAS seleccionado con éxito para la fecha {selected_date}.")
    #                 self.driver.find_element(By.TAG_NAME, "body").click()
    #                 return True

    #             checked_dates += 1
    #             self.client_print_controller(f"Sin éxito en {selected_date} (sin horario o error). Buscando la siguiente fecha disponible...")

    #         self.warning_controller(f"No se encontraron horarios CAS con disponibilidad tras revisar todas las fechas posibles (Máx {max_dates_to_check}).")
    #         return False
            
    #     except Exception as e:
    #         self.error_controller(f"Error general durante la verificación de fechas CAS: {e}")
    #         return False

    # def auto_select_date(self, month, day):
    #     try:
    #         time_select = self.driver.find_element(By.ID, "appointments_consulate_appointment_time")
    #         self.auto_select_option(time_select)
    #         self.driver.find_element(By.TAG_NAME, "body").click()
            
    #         cas_ready = self.CheckCASDateColombia()
            
    #         if not cas_ready:
    #             self.warning_controller("Se detiene el proceso de auto programación por falta de horarios CAS disponibles válidos.")
    #             return False
                
    #         self.auto_submit_reprogramacion_cita(self, month, day)
    #         return True
            
    #     except Exception as e:
    #         self.error_controller(f"Error en auto_select_date: {e}")
    #         return False
    # -------------------------
    # Database helpers (Supabase or local processes.json fallback)
    # -------------------------
    def _update_process_record(self, update_data: dict) -> bool:
        """Intenta actualizar el registro del proceso en Supabase. Si falla,
        aplica cambios en el archivo local processes.json como fallback."""
        try:
            if update_record:
                update_record('processes', 'appointment_id', self.appointment_id, update_data)
                return True
        except Exception as e:
            self.logger.error(f"Error actualizando DB vía Supabase: {e}")

        # Fallback local file update
        try:
            file_path = 'processes.json'
            processes = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    processes = json.load(f)

            matched = False
            for proc in processes:
                if str(proc.get('appointment_id')) == str(self.appointment_id) or str(proc.get('process_id')) == str(self.appointment_id):
                    proc.update(update_data)
                    matched = True
                    break

            if not matched:
                new_proc = {'appointment_id': self.appointment_id}
                new_proc.update(update_data)
                processes.append(new_proc)

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(processes, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            self.logger.error(f"Error actualizando processes.json local: {e}")
            return False

    def _fetch_process_record(self):
        try:
            if read_records:
                res = read_records('processes', {'appointment_id': self.appointment_id})
                # Intentar interpretar la respuesta de varias formas
                data = None
                if isinstance(res, dict) and 'data' in res:
                    data = res.get('data')
                elif hasattr(res, 'data'):
                    data = getattr(res, 'data')
                else:
                    try:
                        data = res[0]
                    except Exception:
                        data = None

                if isinstance(data, list) and len(data) > 0:
                    return data[0]
                return data

            # Fallback local file
            file_path = 'processes.json'
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    processes = json.load(f)
                for proc in processes:
                    if str(proc.get('appointment_id')) == str(self.appointment_id) or str(proc.get('process_id')) == str(self.appointment_id):
                        return proc
        except Exception as e:
            self.logger.error(f"Error obteniendo registro de proceso: {e}")
        return None

    def _reset_process_error_history(self):
        try:
            self._update_process_record({'error_history': []})
        except Exception as e:
            self.logger.error(f"Error reseteando error_history: {e}")

    def _append_process_error(self, error_message: str):
        try:
            proc = self._fetch_process_record()
            existing = []
            if proc and isinstance(proc.get('error_history'), list):
                existing = proc.get('error_history')
            existing.append(error_message)
            self._update_process_record({'error_history': existing})
        except Exception as e:
            self.logger.error(f"Error guardando historial de error: {e}")

    def _mark_process_autoprogrammed(self, date_str: str):
        try:
            self._update_process_record({'process_finished': True, 'process_new_appointment_date': date_str})
        except Exception as e:
            self.logger.error(f"Error marcando proceso como autoprogramado: {e}")

    def _get_selected_date_value(self):
        try:
            candidates = ["appointments_consulate_appointment_date", "appointments_asc_appointment_date"]
            for cid in candidates:
                els = self.driver.find_elements(By.ID, cid)
                if els:
                    val = els[0].get_attribute('value')
                    if val:
                        return val
        except Exception:
            pass
        return None


    def auto_submit_reprogramacion_cita(self, month, day):
        try:
            self.driver.find_element(By.TAG_NAME, "body").click()
             # Dar click en el botón de envío (input con id appointments_submit)
            submit_button = self.driver.find_element(By.ID, "appointments_submit")
            submit_button.click()
            self.client_print_controller(f"Cita lista para programar en {self.location} para {month} {day}")
            if self.auto_programacion_allowed == False:
                # 1. Mandar correo de alerta de que se encontró cita (pero no se programará)
                recipients = self.user_email_alert if self.user_email_alert else ""
                alert_system = EmailAlert(recipients)
                
                alert_system.send_email_alert(f"CITA CONSULAR ENCONTRADA (No autoprogramada) para {self.email} ", month, day, self.location, user_id=self.user_id)
                self.client_print_controller("Se mandó la alerta al correo de la cuenta, pero no se hizo la autoprogramación porque está desactivada.")
                try:
                    selected_val = self.consular_appointment_date_confirmed
                    if selected_val:
                        self._mark_process_autoprogrammed(selected_val)
                    else:
                        self._mark_process_autoprogrammed(f"{month} {day}")
                except Exception:
                    pass
                sys.exit()
            
            #Dar click en el enlace (a) con la clase "button alert"
            #CUIDADO QUE ESCOGE CITA
            alert_button = self.driver.find_element(By.CSS_SELECTOR, "a.button.alert")
            alert_button.click()
            time.sleep(10)
          
            self.client_print_controller(f"Cita escogida con EXITO en {self.location} para {month} {day}")
            self.warning_controller(f"FECHA SELECCIONADA Y ALERTA  {month} el {day} en {self.location}")
            recipients = self.user_email_alert if self.user_email_alert else ""
            alert_system = EmailAlert(recipients)
            alert_system.send_email_alert(f"CITA AUTO PROGRAMADA! para {self.email} ", month, day, self.location, user_id=self.user_id)

            # Marcar proceso como autoprogramado en DB (si es posible)
            try:
                selected_val = self.consular_appointment_date_confirmed
                if selected_val:
                    self._mark_process_autoprogrammed(selected_val)
                else:
                    self._mark_process_autoprogrammed(f"{month} {day}")
            except Exception:
                pass

            time.sleep(45)
            sys.exit()
        except Exception as e:
            self.error_controller(f"Error en autoSelectDate: {e}")



