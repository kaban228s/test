import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import argparse
import os
from pathlib import Path



class ImageEnhancer:
    def __init__(self):
        pass
    
    def enhance_sharpness(self, image, factor=2.0):
        """Повышение четкости изображения"""
        if isinstance(image, np.ndarray):
            # OpenCV метод - унशарп маскинг
            gaussian = cv2.GaussianBlur(image, (0, 0), 2.0)
            unsharp_mask = cv2.addWeighted(image, 1.0 + factor, gaussian, -factor, 0)
            return unsharp_mask
        else:
            # PIL метод
            enhancer = ImageEnhance.Sharpness(image)
            return enhancer.enhance(factor)
    
    def enhance_contrast(self, image, factor=1.5):
        """Улучшение контраста"""
        if isinstance(image, np.ndarray):
            # OpenCV метод с CLAHE
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=factor, tileGridSize=(8,8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        else:
            # PIL метод
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(factor)
    
    def adjust_brightness(self, image, factor=1.2):
        """Регулировка яркости"""
        if isinstance(image, np.ndarray):
            # OpenCV метод
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            v = cv2.multiply(v, factor)
            v = np.clip(v, 0, 255).astype(np.uint8)
            enhanced = cv2.merge([h, s, v])
            return cv2.cvtColor(enhanced, cv2.COLOR_HSV2BGR)
        else:
            # PIL метод
            enhancer = ImageEnhance.Brightness(image)
            return enhancer.enhance(factor)
    
    def denoise(self, image):
        """Шумоподавление"""
        if isinstance(image, np.ndarray):
            # OpenCV метод
            return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        else:
            # PIL метод
            return image.filter(ImageFilter.MedianFilter(size=3))
    
    def enhance_text_readability(self, image):
        """Улучшение читаемости текста"""
        if isinstance(image, np.ndarray):
            # Преобразование в оттенки серого
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Применение адаптивной бинаризации
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                         cv2.THRESH_BINARY, 11, 2)
            
            # Морфологические операции для улучшения текста
            kernel = np.ones((2,2), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            
            # Преобразование обратно в цветное изображение
            return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        else:
            # PIL метод
            # Преобразование в оттенки серого
            gray = image.convert('L')
            
            # Повышение контраста
            enhancer = ImageEnhance.Contrast(gray)
            enhanced = enhancer.enhance(2.0)
            
            # Преобразование обратно в RGB
            return enhanced.convert('RGB')
    
    def upscale_image(self, image, scale_factor=2):
        """Увеличение разрешения изображения"""
        if isinstance(image, np.ndarray):
            height, width = image.shape[:2]
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        else:
            width, height = image.size
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            return image.resize((new_width, new_height), Image.LANCZOS)
    
    def enhance_bill_document(self, image):
        """Специальная обработка для документов типа счетов"""
        # Конвертация в оттенки серого
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Увеличение контраста с более агрессивными параметрами
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Гауссово размытие для уменьшения шума
        blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)
        
        # Адаптивная бинаризация для четкого текста
        binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 15, 10)
        
        # Морфологические операции для улучшения структуры текста
        # Убираем мелкие точки (шум)
        kernel_clean = np.ones((2,2), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_clean)
        
        # Соединяем разорванные части символов
        kernel_connect = np.ones((3,3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_connect)
        
        # Утолщаем тонкие линии текста
        kernel_dilate = np.ones((2,2), np.uint8)
        binary = cv2.dilate(binary, kernel_dilate, iterations=1)
        
        # Преобразование обратно в цветное для совместимости
        result = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        
        return result
    
    def process_specific_bill(self):
        """Специальная функция для обработки файла счета_page0.jpg"""
        input_path = "output_images/счета_page0.jpg"
        output_path = "enhanced_счета_page0.jpg"
        
        try:
            # Проверяем существование файла
            if not os.path.exists(input_path):
                print(f"Файл не найден: {input_path}")
                return False
            
            # Загружаем изображение
            image = cv2.imread(input_path)
            if image is None:
                print(f"Не удалось загрузить изображение: {input_path}")
                return False
            
            print(f"Начинаем улучшение документа: {input_path}")
            
            # Применяем специальную обработку для документов
            enhanced_image = self.enhance_bill_document(image)
            
            # Дополнительно повышаем четкость
            enhanced_image = self.enhance_sharpness(enhanced_image, factor=2.0)
            
            # Сохраняем результат
            cv2.imwrite(output_path, enhanced_image)
            print(f"Улучшенный документ сохранен: {output_path}")
            
            # Также сохраняем копию с увеличенным разрешением
            upscaled_output = "enhanced_upscaled_счета_page0.jpg"
            upscaled_image = self.upscale_image(enhanced_image, scale_factor=2)
            cv2.imwrite(upscaled_output, upscaled_image)
            print(f"Увеличенная версия сохранена: {upscaled_output}")
            
            return True
            
        except Exception as e:
            print(f"Ошибка при обработке документа: {e}")
            return False
    
    def process_image(self, input_path, output_path, enhance_text=False, upscale=False):
        """Обработка одного изображения с применением всех улучшений"""
        try:
            # Загрузка изображения
            image = cv2.imread(input_path)
            if image is None:
                print(f"Не удалось загрузить изображение: {input_path}")
                return False
            
            print(f"Обрабатываем: {input_path}")
            
            # Применение улучшений
            image = self.denoise(image)
            image = self.enhance_contrast(image, factor=1.3)
            image = self.adjust_brightness(image, factor=1.1)
            image = self.enhance_sharpness(image, factor=1.5)
            
            if enhance_text:
                image = self.enhance_text_readability(image)
            
            if upscale:
                image = self.upscale_image(image, scale_factor=2)
            
            # Сохранение результата
            cv2.imwrite(output_path, image)
            print(f"Сохранено: {output_path}")
            return True
            
        except Exception as e:
            print(f"Ошибка при обработке {input_path}: {e}")
            return False
    
    def process_directory(self, input_dir, output_dir, enhance_text=False, upscale=False, keep_names=False):
        """Обработка всех изображений в директории"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        # Создание выходной директории
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Поддерживаемые форматы
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
        processed_count = 0
        for file_path in input_path.rglob('*'):
            if file_path.suffix.lower() in supported_formats:
                # Создание пути для выходного файла
                relative_path = file_path.relative_to(input_path)
                if keep_names:
                    # Сохраняем оригинальное имя файла
                    out_file = output_path / relative_path.name
                else:
                    # Добавляем префикс enhanced_
                    out_file = output_path / f"enhanced_{relative_path.name}"
                
                if self.process_image(str(file_path), str(out_file), enhance_text, upscale):
                    processed_count += 1
        
        print(f"Обработано изображений: {processed_count}")

def main():
    parser = argparse.ArgumentParser(description='Улучшение четкости и читаемости изображений')
    parser.add_argument('input', nargs='?', help='Путь к изображению или директории')
    parser.add_argument('-o', '--output', help='Путь для сохранения результата')
    parser.add_argument('--text', action='store_true', 
                       help='Включить специальную обработку для текста')
    parser.add_argument('--upscale', action='store_true', 
                       help='Увеличить разрешение изображения в 2 раза')
    parser.add_argument('--bill', action='store_true',
                       help='Обработать специальный файл счета_page0.jpg')
    parser.add_argument('--keep-names', action='store_true',
                       help='Сохранить оригинальные имена файлов без префикса enhanced_')
    
    args = parser.parse_args()
    
    enhancer = ImageEnhancer()
    
    # Проверяем флаг для обработки конкретного счета
    if args.bill:
        enhancer.process_specific_bill()
        return
    
    # Если не указан путь и нет флага --bill, показываем справку
    if not args.input:
        parser.print_help()
        return
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Обработка одного файла
        if args.output:
            output_path = args.output
        else:
            output_path = f"enhanced_{input_path.name}"
        
        enhancer.process_image(str(input_path), output_path, args.text, args.upscale)
        
    elif input_path.is_dir():
        # Обработка директории
        if args.output:
            output_dir = args.output
        else:
            output_dir = "enhanced_images"
        
        enhancer.process_directory(str(input_path), output_dir, args.text, args.upscale, args.keep_names)
        
    else:
        print(f"Указанный путь не существует: {args.input}")

if __name__ == "__main__":
    main()



