import smtplib
from email.message import EmailMessage
from gmail_credentials import SENDER_EMAIL, PASSWORD, RECIPIENT_EMAIL

class EmailAlert:
    def __init__(self):
        """
        Inicializa el sistema de alertas con credenciales desde archivo
        """
        self.sender_email = SENDER_EMAIL
        self.sender_password = PASSWORD
        self.recipient_email = RECIPIENT_EMAIL

    def send_email_alert(self, title: str, month: str, day: str, location: str) -> None:
        """
        Envía alerta de cita disponible por email
        """
        msg = EmailMessage()
        msg['Subject'] = f"{title} el {day} de {month} en {location}"
        msg['From'] = self.sender_email
        msg['To'] = self.recipient_email
        msg.set_content(
            f"¡{title}!\n\n"
            f"Fecha: {day} de {month}\n"
            f"Ubicación: {location}\n\n"
        )

        # Enviar email con conexión segura
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
                print("Alerta enviada exitosamente!")
        except Exception as e:
            print(f"Error enviando email: {str(e)}")

# if __name__ == "__main__":
#     alert_system = EmailAlert()
#     alert_system.send_email_alert(
#         month="Julio",
#         day="15",
#         location="Madrid Centro"
#     )