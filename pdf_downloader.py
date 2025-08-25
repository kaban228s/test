# #!/usr/bin/env python3
# """
# PDF Email Downloader
# Скачивает PDF файлы из писем
# """
#
# import imaplib
# import email
# import logging
# import hashlib
# import time
# from datetime import datetime
# from pathlib import Path
# import json
#
#
# class PDFEmailDownloader:
#     def __init__(self, config_path="config.json"):
#         """Инициализация с загрузкой конфигурации"""
#         self.config = self.load_config(config_path)
#         self.setup_logging()
#         self.downloads_dir = Path("downloads")
#         self.downloads_dir.mkdir(exist_ok=True)
#         self.processed_file = Path("processed_emails.json")
#         self.processed_emails = self.load_processed_emails()
#
#     def load_config(self, config_path):
#         """Загрузка конфигурации из JSON файла"""
#         try:
#             with open(config_path, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         except FileNotFoundError:
#             logging.error(f"Файл конфигурации {config_path} не найден")
#             return {}
#
#     def load_processed_emails(self):
#         """Загрузка списка уже обработанных писем"""
#         try:
#             with open(self.processed_file, 'r', encoding='utf-8') as f:
#                 return set(json.load(f))
#         except FileNotFoundError:
#             return set()
#
#     def save_processed_emails(self):
#         """Сохранение списка обработанных писем"""
#         with open(self.processed_file, 'w', encoding='utf-8') as f:
#             json.dump(list(self.processed_emails), f, indent=2)
#
#     def get_email_hash(self, email_message):
#         """Создание уникального хеша письма"""
#         message_id = email_message.get('Message-ID', '')
#         subject = email_message.get('Subject', '')
#         from_addr = email_message.get('From', '')
#         date = email_message.get('Date', '')
#
#         hash_string = f"{message_id}|{subject}|{from_addr}|{date}"
#         return hashlib.md5(hash_string.encode('utf-8')).hexdigest()
#
#     def setup_logging(self):
#         """Настройка логирования"""
#         log_dir = Path("logs")
#         log_dir.mkdir(exist_ok=True)
#
#         logging.basicConfig(
#             level=logging.INFO,
#             format='%(asctime)s - %(levelname)s - %(message)s',
#             handlers=[
#                 logging.FileHandler(log_dir / "pdf_downloader.log", encoding='utf-8'),
#                 logging.StreamHandler()
#             ]
#         )
#
#     def connect_to_email(self, max_retries=3, retry_delay=5):
#         """Подключение к почтовому серверу с переподключением"""
#         for attempt in range(max_retries):
#             try:
#                 mail = imaplib.IMAP4_SSL(self.config['imap_server'], self.config.get('imap_port', 993))
#                 mail.login(self.config['email'], self.config['password'])
#                 logging.info("Успешное подключение к почтовому серверу")
#                 return mail
#             except Exception as e:
#                 logging.error(f"Ошибка подключения к почте (попытка {attempt + 1}/{max_retries}): {e}")
#                 if attempt < max_retries - 1:
#                     logging.info(f"Повторная попытка через {retry_delay} секунд")
#                     time.sleep(retry_delay)
#                     retry_delay *= 2  # Экспоненциальная задержка
#         return None
#
#     def search_emails(self, mail, criteria="ALL"):
#         """Поиск писем по критерию"""
#         try:
#             mail.select('inbox')
#             status, messages = mail.search(None, criteria)
#             if status == 'OK':
#                 email_ids = messages[0].split()
#                 logging.info(f"Найдено {len(email_ids)} писем")
#                 return email_ids
#             return []
#         except Exception as e:
#             logging.error(f"Ошибка поиска писем: {e}")
#             return []
#
#     def download_pdf_attachments(self, mail, email_ids):
#         """Скачивание PDF вложений из писем"""
#         pdf_count = 0
#         new_emails_count = 0
#
#         for email_id in email_ids:
#             try:
#                 status, msg_data = mail.fetch(email_id, '(RFC822)')
#                 if status != 'OK':
#                     continue
#
#                 email_body = msg_data[0][1]
#                 email_message = email.message_from_bytes(email_body)
#
#                 email_hash = self.get_email_hash(email_message)
#
#                 if email_hash in self.processed_emails:
#                     logging.info(f"Письмо уже обработано, пропускаем: {email_message.get('Subject', 'Без темы')}")
#                     continue
#
#                 subject = email_message['Subject'] or "Без темы"
#                 logging.info(f"Обработка нового письма: {subject}")
#                 new_emails_count += 1
#
#                 has_pdf = False
#                 for part in email_message.walk():
#                     if part.get_content_disposition() == 'attachment':
#                         filename = part.get_filename()
#                         if filename and filename.lower().endswith('.pdf'):
#                             pdf_count += 1
#                             has_pdf = True
#                             safe_filename = self.create_safe_filename(filename, pdf_count)
#                             filepath = self.downloads_dir / safe_filename
#
#                             with open(filepath, 'wb') as f:
#                                 f.write(part.get_payload(decode=True))
#
#                             logging.info(f"Скачан PDF: {safe_filename}")
#                             print(f"Скачан: {safe_filename}")
#
#                 self.processed_emails.add(email_hash)
#
#             except Exception as e:
#                 logging.error(f"Ошибка обработки письма {email_id}: {e}")
#
#         if new_emails_count > 0:
#             self.save_processed_emails()
#             logging.info(f"Обработано новых писем: {new_emails_count}")
#
#         return pdf_count
#
#     def create_safe_filename(self, original_name, counter):
#         """Создание безопасного имени файла"""
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         safe_name = "".join(c for c in original_name if c.isalnum() or c in "._-")
#         return f"{timestamp}_{counter:03d}_{safe_name}"
#
#     def run(self, search_criteria="ALL"):
#         """Основная функция запуска"""
#         if not self.config:
#             print("Ошибка: не найден файл конфигурации config.json")
#             return
#
#         print("Подключение к почтовому серверу...")
#         mail = self.connect_to_email()
#
#         if not mail:
#             print("Ошибка подключения к почте")
#             return
#
#         try:
#             print("Поиск писем...")
#             email_ids = self.search_emails(mail, search_criteria)
#
#             if not email_ids:
#                 print("Письма не найдены")
#                 return
#
#             print(f"Найдено писем: {len(email_ids)}")
#             print("Скачивание PDF файлов...")
#
#             pdf_count = self.download_pdf_attachments(mail, email_ids)
#
#             if pdf_count > 0:
#                 print(f"Скачано PDF файлов: {pdf_count}")
#                 print(f"Файлы сохранены в папку: {self.downloads_dir}")
#             else:
#                 print("PDF файлы не найдены")
#
#         finally:
#             mail.logout()
#             print("Отключение от почтового сервера")
#
#
# if __name__ == "__main__":
#     downloader = PDFEmailDownloader()
#     downloader.run()