#!/usr/bin/env python3
"""
Основной файл для запуска всего пайплайна обработки документов.
Последовательность: Mail_Loader -> pdfconverter -> image_enhancer -> ai_sender
"""

import sys
import logging
from pathlib import Path
import traceback

# Импортируем модули  
import subprocess

def setup_logging():
    """Настройка логирования для main.py"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [MAIN] - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('main_pipeline.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def run_Mail_Loader():
    """Запуск загрузчика почты"""
    logging.info("=== ЭТАП 1: Загрузка писем с вложениями ===")
    try:
        result = subprocess.run([sys.executable, 'Mail_Loader.py'], capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            logging.info(f"Mail_Loader output: {result.stdout}")
            return True
        else:
            logging.error(f"Mail_Loader ошибка: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Ошибка запуска Mail_Loader: {e}")
        logging.error(traceback.format_exc())
        return False

def run_pdfconverter():
    """Запуск конвертера PDF в изображения"""
    logging.info("=== ЭТАП 2: Конвертация PDF в изображения ===")
    try:
        result = subprocess.run([sys.executable, 'pdfconverter.py'], capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            logging.info(f"pdfconverter output: {result.stdout}")
            return True
        else:
            logging.error(f"pdfconverter ошибка: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Ошибка запуска pdfconverter: {e}")
        logging.error(traceback.format_exc())
        return False

def run_image_enhancer():
    """Запуск улучшения изображений"""
    logging.info("=== ЭТАП 3: Улучшение качества изображений ===")
    try:
        result = subprocess.run([
            sys.executable, 'image_enhancer.py', 
            'output_images', 
            '--output', 'enhanced_images',
            '--text',
            '--keep-names'
        ], capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            logging.info(f"image_enhancer output: {result.stdout}")
            return True
        else:
            logging.error(f"image_enhancer ошибка: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Ошибка запуска image_enhancer: {e}")
        logging.error(traceback.format_exc())
        return False

def run_ai_sender():
    """Запуск AI обработки изображений"""
    logging.info("=== ЭТАП 4: AI обработка документов ===")
    try:
        result = subprocess.run([sys.executable, 'Ai_sender.py'], capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            logging.info(f"Ai_sender output: {result.stdout}")
            return True
        else:
            logging.error(f"Ai_sender ошибка: {result.stderr}")
            return False
    except Exception as e:
        logging.error(f"Ошибка запуска Ai_sender: {e}")
        logging.error(traceback.format_exc())
        return False

def main():
    """Главная функция, запускающая весь пайплайн"""
    setup_logging()
    
    logging.info("========== ЗАПУСК ПАЙПЛАЙНА ОБРАБОТКИ ДОКУМЕНТОВ ==========")
    
    steps = [
        ("Загрузка писем", run_Mail_Loader),
        ("Конвертация PDF", run_pdfconverter), 
        ("Улучшение изображений", run_image_enhancer),
        ("AI обработка", run_ai_sender)
    ]
    
    for step_name, step_function in steps:
        logging.info(f"Начинаем: {step_name}")
        
        if not step_function():
            logging.error(f"Ошибка на этапе: {step_name}")
            logging.error("Пайплайн остановлен")
            return False
            
        logging.info(f"Завершено: {step_name}")
        logging.info("-" * 50)
    
    logging.info("========== ПАЙПЛАЙН УСПЕШНО ЗАВЕРШЕН ==========")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
