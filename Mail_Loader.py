import imaplib
import json
import logging
import email
import email.header
import re
from pathlib import Path

# Создание папки для логов
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "mail_loader.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)


def is_pdf_attachment(part):
    """Проверяет, является ли часть PDF-вложением"""
    # Проверяем Content-Type
    if part.get_content_type() == 'application/pdf':
        return True

    # Проверяем по имени файла и disposition
    disposition = part.get_content_disposition()
    if disposition in ['attachment', 'inline']:
        filename = part.get_filename()
        if filename and filename.lower().endswith('.pdf'):
            return True

    return False


def decode_filename(filename):
    """Декодирует имя файла из MIME"""
    if not filename:
        return "unnamed.pdf"

    try:
        parts = email.header.decode_header(filename)
        decoded = ''
        for part, encoding in parts:
            if isinstance(part, bytes):
                decoded += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded += str(part)
        # Убираем недопустимые символы
        return re.sub(r'[<>:"/\\|?*]', '_', decoded)
    except:
        return "unnamed.pdf"



def load_config(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            config.setdefault('imap_server', 'email.sct.ru')
            config.setdefault('max_message_size', 50 * 1024 * 1024)
            return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Ошибка конфигурации: {e}")
        return {}


class ConfigLoader:
    def __init__(self, config_path="config.json"):
        self.config = load_config(config_path)
        self.downloads_dir = Path(self.config.get('downloads_dir', 'downloads'))
        self.downloads_dir.mkdir(exist_ok=True)


class MailConnector:
    def __init__(self, config):
        self.config = config
        self.mail = None

    def connect(self):
        """Подключается и авторизуется"""
        try:
            server = self.config.get('imap_server', 'email.sct.ru')
            self.mail = imaplib.IMAP4_SSL(server)

            typ, data = self.mail.login(self.config['email'], self.config['password'])
            if typ != 'OK':
                logging.error(f"Ошибка авторизации: {data}")
                return False

            logging.info("Успешная авторизация")
            return True
        except Exception as e:
            logging.error(f"Ошибка подключения: {e}")
            return False

    def disconnect(self):
        """Закрывает соединение"""
        if self.mail:
            try:
                self.mail.close()
            except Exception as e:
                logging.warning(f"Ошибка при close(): {e}")

            try:
                self.mail.logout()
                logging.info("Соединение закрыто")
            except Exception as e:
                logging.warning(f"Ошибка при logout(): {e}")


class MailReader:
    def __init__(self, config, mail, downloads_dir):
        self.config = config
        self.mail = mail
        self.downloads_dir = downloads_dir
        self.max_size = config.get('max_message_size', 50 * 1024 * 1024)

    def check_message_size(self, uid):
        """Проверяет размер письма"""
        try:
            typ, data = self.mail.uid('fetch', uid, '(RFC822.SIZE)')
            if typ == 'OK':
                size = int(re.search(r'RFC822.SIZE (\d+)', data[0].decode()).group(1))
                if size > self.max_size:
                    logging.warning(f"Письмо UID {uid.decode()} слишком большое: {size / 1024 / 1024:.1f}MB")
                    return False
            return True
        except:
            return True

    def save_attachment(self, part):
        """Сохраняет вложение"""
        try:
            filename = decode_filename(part.get_filename())
            filepath = self.downloads_dir / filename

            # Делаем имя уникальным
            counter = 1
            while filepath.exists():
                name = filepath.stem
                filepath = self.downloads_dir / f"{name}_{counter}.pdf"
                counter += 1

            payload = part.get_payload(decode=True)
            if payload:
                with open(filepath, 'wb') as f:
                    f.write(payload)
                logging.info(f"Сохранен: {filepath.name}")
                return True
        except Exception as e:
            logging.error(f"Ошибка сохранения: {e}")
        return False

    def process_email(self, uid):
        """Обрабатывает одно письмо"""
        try:
            # Проверяем размер
            if not self.check_message_size(uid):
                return False

            # Загружаем без изменения флагов
            typ, msg_data = self.mail.uid('fetch', uid, '(BODY.PEEK[])')
            if typ != 'OK':
                return False

            email_message = email.message_from_bytes(msg_data[0][1])
            subject = email_message.get('Subject', 'Без темы')
            logging.info(f"Обработка письма: {subject}")

            pdf_found = False
            for part in email_message.walk():
                if is_pdf_attachment(part):
                    if self.save_attachment(part):
                        pdf_found = True

            # Помечает как прочитанное после успешной обработки
            if pdf_found:
                self.mail.uid('store', uid, '+FLAGS', '\\Seen')
                logging.info("Письмо помечено как прочитанное")

            return True

        except Exception as e:
            logging.error(f"Ошибка обработки письма: {e}")
            return False

    def process_all_unread(self):
        """Обрабатывает все непрочитанные письма"""
        self.mail.select("INBOX")

        # Используем UID для поиска
        typ, data = self.mail.uid('search', None, 'UNSEEN')
        if typ != 'OK':
            logging.error("Ошибка поиска писем")
            return

        uid_list = data[0].split()
        if not uid_list:
            print("Новых писем нет")
            return

        print(f"Найдено {len(uid_list)} непрочитанных писем")

        processed = 0
        for uid in uid_list:
            if self.process_email(uid):
                processed += 1

        print(f"Обработано писем: {processed}")


def main():
    config_loader = ConfigLoader()

    if not config_loader.config or 'email' not in config_loader.config:
        print("Ошибка: проверьте config.json")
        return

    mail_connector = MailConnector(config_loader.config)

    try:
        if not mail_connector.connect():
            return

        mail_reader = MailReader(
            config_loader.config,
            mail_connector.mail,
            config_loader.downloads_dir
        )

        mail_reader.process_all_unread()

    finally:
        mail_connector.disconnect()


if __name__ == "__main__":
    main()