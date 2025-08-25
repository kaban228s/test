import imaplib
import json
import logging
import email
from pathlib import Path


def load_config(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Файл конфигурации {config_path} не найден")
        return {}


class ConfigLoader(object):

    def __init__(self, config_path="config.json"):
        self.config = load_config(config_path)
        self.downloads_dir = Path("downloads")
        self.downloads_dir.mkdir(exist_ok=True)


class MailConnector:

    def __init__(self, config):
        self.config = config
        self.mail = imaplib.IMAP4_SSL(self.config['imap_server'])
        self.mail.login(self.config['email'], self.config['password'])

class MailReader:
    def __init__(self, config, mail, downloads_dir):
        self.config = config
        self.mail = mail
        self.downloads_dir = downloads_dir
        mail.list()
        mail.select("inbox")

    def download_pdf_attachments(self, mail, email_ids):

        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            if status != 'OK':
                continue

            email_body = msg_data[0][1]
            email_message = email.message_from_bytes(email_body)

            subject = email_message['Subject'] or "Без темы"
            logging.info(f"Обработка нового письма: {subject}")

            for part in email_message.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename and any(filename.lower().endswith(ext) for ext in self.config.get('allowed_extensions', ['.pdf'])):
                        safe_filename = filename
                        filepath = self.downloads_dir / safe_filename

                        with open(filepath, 'wb') as f:
                            f.write(part.get_payload(decode=True))

                        logging.info(f"Скачан PDF: {safe_filename}")
                        print(f"Скачан: {safe_filename}")

if __name__ == "__main__":
    config_loader = ConfigLoader()

    mail_connector = MailConnector(config_loader.config)

    mail_reader = MailReader(config_loader.config, mail_connector.mail, config_loader.downloads_dir)

    status, messages = mail_connector.mail.search(None, 'UNSEEN')
    if status == 'OK':
        email_ids = messages[0].split()
        if email_ids:
            print(f"Найдено {len(email_ids)} непрочитанных писем")
            mail_reader.download_pdf_attachments(mail_connector.mail, email_ids)
        else:
            print("Новых писем нет")
    else:
        print("ошибка поиска писем")