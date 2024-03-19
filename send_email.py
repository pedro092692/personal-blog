import smtplib
from dotenv import load_dotenv
import os


class Email:

    def __init__(self):
        load_dotenv()
        self.user = os.getenv('USER_EMAIL')
        self.password = os.getenv('PASSWORD_EMAIL')
        self.port = os.getenv('EMAIL_PORT')
        self.server = os.getenv('EMAIL_SERVER')

    def send_email(self, message: str):
        try:
            with smtplib.SMTP(self.server, self.port) as connection:
                connection.starttls()
                connection.login(self.user, self.password)
                connection.sendmail(to_addrs=[self.user], from_addr=self.user,
                                    msg=f'Subject: Message from you personal blog'
                                    f"\n\n{message}")
                return True

        except smtplib.SMTPException as e:
            print(f'There was a problem trying to connect with the email server: {e}')
            return False
