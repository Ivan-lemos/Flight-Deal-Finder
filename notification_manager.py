import smtplib
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# ---------------------------- CLASSES DE SERVIÇO DE NOTIFICAÇÃO ------------------------------- #

class EmailService:
    """Serviço responsável pelo envio de e-mails.

    Encapsula a lógica de conexão e envio de e-mails via SMTP.
    """
    def __init__(self, smtp_address: str, email: str, password: str):
        """Inicializa o serviço de e-mail.

        Args:
            smtp_address (str): Endereço do servidor SMTP.
            email (str): Endereço de e-mail do remetente.
            password (str): Senha do e-mail do remetente.
        """
        self.smtp_address = smtp_address
        self.email = email
        self.password = password

    def send_email(self, to_addrs: str, subject: str, body: str) -> None:
        """Envia um e-mail para um destinatário específico.

        Args:
            to_addrs (str): Endereço de e-mail do destinatário.
            subject (str): Assunto do e-mail.
            body (str): Corpo do e-mail.
        """
        try:
            with smtplib.SMTP(self.smtp_address) as connection:
                connection.starttls()  # Inicia a segurança TLS
                connection.login(self.email, self.password)
                msg = f"Subject:{subject}\n\n{body}".encode('utf-8')
                connection.sendmail(
                    from_addr=self.email,
                    to_addrs=to_addrs,
                    msg=msg
                )
            print(f"E-mail enviado para {to_addrs} com sucesso.")
        except smtplib.SMTPException as e:
            print(f"Erro SMTP ao enviar e-mail para {to_addrs}: {e}")
        except Exception as e:
            print(f"Erro inesperado ao enviar e-mail para {to_addrs}: {e}")


class SMSService:
    """Serviço responsável pelo envio de mensagens SMS via Twilio.

    Encapsula a lógica de conexão e envio de SMS usando a API Twilio.
    """
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        """Inicializa o serviço de SMS.

        Args:
            account_sid (str): SID da conta Twilio.
            auth_token (str): Token de autenticação Twilio.
            from_number (str): Número de telefone Twilio remetente.
        """
        self.client = Client(account_sid, auth_token)
        self.from_number = from_number

    def send_sms(self, to_number: str, message_body: str) -> None:
        """Envia uma mensagem SMS para um número de telefone específico.

        Args:
            to_number (str): Número de telefone do destinatário.
            message_body (str): Corpo da mensagem SMS.
        """
        try:
            message = self.client.messages.create(
                from_=self.from_number,
                body=message_body,
                to=to_number
            )
            print(f"SMS enviado para {to_number} com SID: {message.sid}")
        except TwilioRestException as e:
            print(f"Erro Twilio ao enviar SMS para {to_number}: {e}")
        except Exception as e:
            print(f"Erro inesperado ao enviar SMS para {to_number}: {e}")


class WhatsAppService(SMSService):
    """Serviço responsável pelo envio de mensagens WhatsApp via Twilio.

    Herda de SMSService, pois a lógica de envio é similar, mas com prefixo 'whatsapp:'.
    """
    def __init__(self, account_sid: str, auth_token: str, from_whatsapp_number: str):
        """Inicializa o serviço de WhatsApp.

        Args:
            account_sid (str): SID da conta Twilio.
            auth_token (str): Token de autenticação Twilio.
            from_whatsapp_number (str): Número de telefone Twilio remetente para WhatsApp (com prefixo 'whatsapp:').
        """
        super().__init__(account_sid, auth_token, f"whatsapp:{from_whatsapp_number}")

    def send_whatsapp(self, to_whatsapp_number: str, message_body: str) -> None:
        """Envia uma mensagem WhatsApp para um número de telefone específico.

        Args:
            to_whatsapp_number (str): Número de telefone do destinatário (com prefixo 'whatsapp:').
            message_body (str): Corpo da mensagem WhatsApp.
        """
        try:
            message = self.client.messages.create(
                from_=self.from_number,
                body=message_body,
                to=f"whatsapp:{to_whatsapp_number}"
            )
            print(f"WhatsApp enviado para {to_whatsapp_number} com SID: {message.sid}")
        except TwilioRestException as e:
            print(f"Erro Twilio ao enviar WhatsApp para {to_whatsapp_number}: {e}")
        except Exception as e:
            print(f"Erro inesperado ao enviar WhatsApp para {to_whatsapp_number}: {e}")


# ---------------------------- CLASSE NotificationManager ------------------------------- #

class NotificationManager:
    """Gerencia o envio de diferentes tipos de notificações (e-mail, SMS, WhatsApp).

    Esta classe atua como um orquestrador, utilizando os serviços de notificação
    apropriados para enviar mensagens.
    """

    def __init__(self):
        """Inicializa o NotificationManager, configurando os serviços de notificação.

        As credenciais são carregadas de variáveis de ambiente.
        """
        # Carrega variáveis de ambiente. Levanta erro se alguma estiver faltando.
        self.smtp_address = os.environ.get("EMAIL_PROVIDER_SMTP_ADDRESS")
        self.email = os.environ.get("MY_EMAIL")
        self.email_password = os.environ.get("MY_EMAIL_PASSWORD")
        self.twilio_sid = os.environ.get("TWILIO_SID")
        self.twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.twilio_virtual_number = os.environ.get("TWILIO_VIRTUAL_NUMBER")
        self.twilio_verified_number = os.environ.get("TWILIO_VERIFIED_NUMBER")
        self.whatsapp_number = os.environ.get("TWILIO_WHATSAPP_NUMBER")

        # Verifica se todas as variáveis de ambiente necessárias estão presentes
        required_env_vars = [
            self.smtp_address, self.email, self.email_password,
            self.twilio_sid, self.twilio_auth_token,
            self.twilio_virtual_number, self.twilio_verified_number, self.whatsapp_number
        ]
        if not all(required_env_vars):
            raise ValueError("Uma ou mais variáveis de ambiente para notificação não estão configuradas. Verifique .env ou variáveis do sistema.")

        # Inicializa os serviços de notificação
        self.email_service = EmailService(self.smtp_address, self.email, self.email_password)
        self.sms_service = SMSService(self.twilio_sid, self.twilio_auth_token, self.twilio_virtual_number)
        self.whatsapp_service = WhatsAppService(self.twilio_sid, self.twilio_auth_token, self.whatsapp_number)

    def send_emails(self, email_list: list[str], subject: str, body: str) -> None:
        """Envia um e-mail para uma lista de destinatários.

        Args:
            email_list (list[str]): Lista de endereços de e-mail dos destinatários.
            subject (str): Assunto do e-mail.
            body (str): Corpo do e-mail.
        """
        print(f"Enviando e-mails para {len(email_list)} destinatários...")
        for email in email_list:
            self.email_service.send_email(email, subject, body)

    def send_sms(self, message_body: str) -> None:
        """Envia uma mensagem SMS para o número de telefone verificado.

        Args:
            message_body (str): Corpo da mensagem SMS.
        """
        print(f"Enviando SMS para {self.twilio_verified_number}...")
        self.sms_service.send_sms(self.twilio_verified_number, message_body)

    def send_whatsapp(self, message_body: str) -> None:
        """Envia uma mensagem WhatsApp para o número de telefone verificado.

        Args:
            message_body (str): Corpo da mensagem WhatsApp.
        """
        print(f"Enviando WhatsApp para {self.twilio_verified_number}...")
        self.whatsapp_service.send_whatsapp(self.twilio_verified_number, message_body)

# Exemplo de uso (pode ser removido se este arquivo for apenas um módulo)
if __name__ == "__main__":
    # Para testar, você precisará configurar as variáveis de ambiente:
    # EMAIL_PROVIDER_SMTP_ADDRESS, MY_EMAIL, MY_EMAIL_PASSWORD
    # TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_VIRTUAL_NUMBER, TWILIO_VERIFIED_NUMBER, TWILIO_WHATSAPP_NUMBER
    try:
        notifier = NotificationManager()

        # Exemplo de envio de e-mail
        # notifier.send_emails(["teste@example.com"], "Assunto de Teste", "Corpo do e-mail de teste.")

        # Exemplo de envio de SMS
        # notifier.send_sms("Esta é uma mensagem de teste SMS.")

        # Exemplo de envio de WhatsApp
        # notifier.send_whatsapp("Esta é uma mensagem de teste WhatsApp.")

    except ValueError as e:
        print(f"Erro de configuração: {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")


