import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone
import json
import os
try:
    from supabase_client import create_record, read_records
except Exception:
    create_record = None
    read_records = None

SENDER_EMAIL = "kevindhuertas@gmail.com"
PASSWORD = "xrbl frzq ugkp ljpt"
DEFAULT_RECIPIENT = "kevindhuertas@gmail.com"
PUNTO_VISAS_EMAIL = "puntovisas.info@gmail.com"


class EmailAlert:
    def __init__(self, recipient_emails=None):
        """
        Inicializa el sistema de alertas con credenciales desde archivo.
        recipient_emails: str or list[str] opcional. Si se proporciona, se usará
        como destinatario(s) además de puntovisas.info@gmail.com.
        """
        self.sender_email = SENDER_EMAIL
        self.sender_password = PASSWORD

        recipients = []
        if recipient_emails:
            if isinstance(recipient_emails, str):
                recipients = [recipient_emails]
            elif isinstance(recipient_emails, (list, tuple)):
                recipients = list(recipient_emails)
        # Asegurar que siempre llegue copia a puntovisas
        if PUNTO_VISAS_EMAIL not in recipients:
            recipients.append(PUNTO_VISAS_EMAIL)
        # Si no hay destinatarios, usar el por defecto
        if not recipients:
            recipients = [DEFAULT_RECIPIENT, PUNTO_VISAS_EMAIL]

        # eliminar duplicados y limpiar espacios
        cleaned = []
        for r in recipients:
            if not r:
                continue
            r = r.strip()
            if r and r not in cleaned:
                cleaned.append(r)

        self.recipient_emails = cleaned

    def _normalize_recipients(self, recipients):
        """Devuelve una lista normalizada (lower, trimmed, sorted)"""
        if not recipients:
            return []
        return sorted([r.strip().lower() for r in recipients if r and r.strip()])

    def _find_recent_duplicate(self, subject: str, body: str, recipients_norm: list):
        """Busca en la tabla 'sent_emails' o en el log local un correo con el mismo subject y recipientes enviado en las ultimas 24h.
        Devuelve el registro coincidente o None."""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        try:
            if read_records:
                res = read_records("sent_emails", {"subject": subject})
                data = None
                if isinstance(res, dict) and "data" in res:
                    data = res.get("data")
                elif hasattr(res, "data"):
                    data = getattr(res, "data")
                else:
                    try:
                        data = res[0]
                    except Exception:
                        data = None

                if isinstance(data, list):
                    for r in data:
                        r_recipients = r.get("recipients") or r.get("recipient_emails") or ""
                        if isinstance(r_recipients, list):
                            r_norm = sorted([x.strip().lower() for x in r_recipients if x])
                        else:
                            r_norm = sorted([x.strip().lower() for x in str(r_recipients).split(",") if x.strip()])

                        if r_norm == recipients_norm:
                            sent_at = r.get("sent_at") or r.get("created_at") or r.get("inserted_at")
                            if sent_at:
                                try:
                                    sent_dt = datetime.fromisoformat(sent_at)
                                    if sent_dt.tzinfo is None:
                                        sent_dt = sent_dt.replace(tzinfo=timezone.utc)
                                    else:
                                        sent_dt = sent_dt.astimezone(timezone.utc)
                                    if sent_dt >= cutoff:
                                        return r
                                except Exception:
                                    # si no podemos parsear la fecha, omitimos ese registro
                                    continue
        except Exception:
            # No queremos que falle por errores de conexión a DB
            pass

        # Fallback: revisar archivo local de logs
        try:
            log_file = os.path.join("logs", "sent_emails.json")
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    entries = json.load(f)
                for r in entries:
                    if r.get("subject") != subject:
                        continue
                    r_recipients = r.get("recipients") or r.get("recipient_emails") or ""
                    if isinstance(r_recipients, list):
                        r_norm = sorted([x.strip().lower() for x in r_recipients if x])
                    else:
                        r_norm = sorted([x.strip().lower() for x in str(r_recipients).split(",") if x.strip()])
                    if r_norm == recipients_norm:
                        sent_at = r.get("sent_at") or r.get("attempted_at")
                        if sent_at:
                            try:
                                sent_dt = datetime.fromisoformat(sent_at)
                                if sent_dt.tzinfo is None:
                                    sent_dt = sent_dt.replace(tzinfo=timezone.utc)
                                else:
                                    sent_dt = sent_dt.astimezone(timezone.utc)
                                if sent_dt >= cutoff:
                                    return r
                            except Exception:
                                continue
        except Exception:
            pass

        return None

    def _log_email(self, record: dict):
        """Intenta guardar el registro en la DB (tabla 'sent_emails'), si falla lo guarda localmente en logs/sent_emails.json"""
        # Añadir timestamp si no existe
        if not record.get("sent_at"):
            record["sent_at"] = datetime.now(timezone.utc).isoformat()
        try:
            if create_record:
                create_record("sent_emails", record)
                return True
        except Exception as e:
            print(f"Error guardando registro en DB: {e}")
        # fallback local
        try:
            os.makedirs("logs", exist_ok=True)
            log_file = os.path.join("logs", "sent_emails.json")
            entries = []
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8") as f:
                    try:
                        entries = json.load(f)
                    except Exception:
                        entries = []
            entries.append(record)
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error guardando registro localmente: {e}")
        return False

    def send_email_alert(self, title: str, month: str, day: str, location: str, user_id: str = None) -> None:
        """
        Envía alerta de cita disponible por email a self.recipient_emails. Antes de enviar,
        revisa en la tabla 'sent_emails' si ya se envió un correo con el mismo subject+recipientes
        en las últimas 24 horas. Si existe, no envía el correo y notifica al administrador.
        """
        subject = f"{title} el {day} de {month} en {location}"
        body = (
            f"¡{title}!\n\n"
            f"Fecha: {day} de {month}\n"
            f"Ubicación: {location}\n\n"
        )

        recipients = self.recipient_emails or []
        recipients_norm = self._normalize_recipients(recipients)

        try:
            # 1) Verificar si ya se envió algo igual en las últimas 24 horas
            duplicate = self._find_recent_duplicate(subject, body, recipients_norm)
            if duplicate:
                # Notificar al administrador y NO reenviar el correo
                admin_msg = EmailMessage()
                admin_msg["Subject"] = f"Intento de envío duplicado: {subject}"
                admin_msg["From"] = self.sender_email
                admin_msg["To"] = SENDER_EMAIL
                admin_body = (
                    f"Se intentó enviar un correo que ya fue enviado en las últimas 24 horas.\n\n"
                    f"User ID: {user_id}\n"
                    f"Destinatarios intentados: {recipients}\n"
                    f"Asunto: {subject}\n\n"

                    f"Cuerpo:\n{body}\n\n"
                    f"Intento realizado en: {datetime.now(timezone.utc).isoformat()}\n\n"
                    f"Registro coincidente encontrado:\n{json.dumps(duplicate, default=str, ensure_ascii=False, indent=2)}\n"
                )
                admin_msg.set_content(admin_body)
                try:
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                        server.login(self.sender_email, self.sender_password)
                        server.send_message(admin_msg, from_addr=self.sender_email, to_addrs=[SENDER_EMAIL])
                        print("Notificación de intento duplicado enviada a:", SENDER_EMAIL)
                except Exception as e:
                    print(f"Error enviando notificación admin: {e}")

                # Guardar intento fallido como registro (opcional)
                try:
                    rec = {
                        "user_id": user_id,
                        "recipients": recipients,
                        "subject": subject,
                        "body": body,
                        "sent": False,
                        "note": "duplicate_attempt",
                        "attempted_at": datetime.now(timezone.utc).isoformat(),
                    }
                    self._log_email(rec)
                except Exception:
                    pass
                return
        except Exception as e:
            print(f"Error al enviar email del duplicado: {e}")


        # Enviar email con conexión segura
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.sender_email
        msg["To"] = ", ".join(recipients)
        msg.set_content(body)
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg, from_addr=self.sender_email, to_addrs=recipients)
                print("Alerta enviada exitosamente a:", recipients)

            # Guardar registro de envío
            try:
                rec = {
                    "user_id": user_id,
                    "recipients": recipients,
                    "subject": subject,
                    "body": body,
                    "sent": True,
                    "sent_at": datetime.now(timezone.utc).isoformat(),
                }
                self._log_email(rec)
            except Exception as e:
                print(f"Error guardando registro tras envío: {e}")
        except Exception as e:
            print(f"Error enviando email: {str(e)}")

# if __name__ == "__main__":
#     alert_system = EmailAlert()
#     alert_system.send_email_alert(
#         month="Julio",
#         day="15",
#         location="Madrid Centro"
#     )