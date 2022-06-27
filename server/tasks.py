import logging
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from huey import SqliteHuey
from .utils import AppConfig


CONFIG = AppConfig()


class CustomHuey(SqliteHuey):
    def __init__(self, name='huey', db_file='tasks.db'):
        self.filename = db_file
        self.logger = logging.getLogger('huey')
        super(CustomHuey, self).__init__(name, filename=db_file)


huey = CustomHuey()

@huey.task()
def send_download_link(recipient, name, url):
    smtp_delivery(recipient, name, url)
    return True


def smtp_delivery(recipient, name, url):
    smtp_config = CONFIG['smtp']

    message = MIMEMultipart()
    message['From'] = '{} <{}>'.format(smtp_config['from_name'], smtp_config['from_address'])
    message['To'] = '{} <{}>'.format(name, recipient)
    message['Subject'] = smtp_config['subject']
    message.attach(MIMEText(url, 'plain'))

    try:
        server = smtplib.SMTP(smtp_config['host'], int(smtp_config['port']))
        with server:
            if smtp_config['starttls']:
                context = ssl.create_default_context()
                server.starttls(context=context)
            server.login(smtp_config['user'], smtp_config['password'])
            res = server.sendmail(smtp_config['from_address'], recipient, message.as_string())
            huey.logger.info('email sent: download "{}" to "{} <{}>"'.format(url, name, recipient))
    except Exception as e:
         huey.logger.error(e)
