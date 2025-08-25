import fitz  # PyMuPDF
from PIL import Image
import os
import glob

downloads_folder = 'downloads'
output_folder = 'output_images'

# Создаем папку если её нет
os.makedirs(output_folder, exist_ok=True)

# Находим все PDF файлы в папке downloads
pdf_files = glob.glob(f'{downloads_folder}/*.pdf')

for pdf_path in pdf_files:
    # Получаем имя файла без расширения
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    doc = fitz.open(pdf_path)
    
    for count, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # 2x zoom for better quality
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.save(f'{output_folder}/{pdf_name}_page{count}.jpg', 'JPEG')
    
    doc.close()
    print(f'Конвертирован: {pdf_path}')
