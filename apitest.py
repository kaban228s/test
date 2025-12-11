import base64
import json
import logging
import os
import re
import requests
from dotenv import load_dotenv

# Диагностика окружения
print("=== ДИАГНОСТИКА API КЛЮЧА ===")
print(f"Текущая директория: {os.getcwd()}")
print(f"Файлы в директории: {os.listdir('.')}")

# Проверяем наличие .env файла
env_file_exists = os.path.exists('.env')
print(f"Файл .env существует: {env_file_exists}")

if env_file_exists:
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            env_content = f.read()
        print("Содержимое .env файла:")
        # Показываем содержимое, но скрываем значения ключей
        lines = env_content.strip().split('\n')
        for line in lines:
            if '=' in line:
                key, value = line.split('=', 1)
                print(f"  {key}=***скрыто*** (длина: {len(value)})")
            else:
                print(f"  {line}")
    except Exception as e:
        print(f"Ошибка чтения .env: {e}")

# Загружаем переменные окружения
print("\n=== ЗАГРУЗКА ПЕРЕМЕННЫХ ===")
load_dotenv()

# Проверяем все способы получения API ключа
api_key_from_env = os.getenv('API_KEY')
api_key_from_environ = os.environ.get('API_KEY')

print(
    f"API_KEY из os.getenv(): {api_key_from_env is not None} (длина: {len(api_key_from_env) if api_key_from_env else 0})")
print(
    f"API_KEY из os.environ.get(): {api_key_from_environ is not None} (длина: {len(api_key_from_environ) if api_key_from_environ else 0})")

# Показываем все переменные окружения, содержащие 'API'
print("\nВсе переменные окружения с 'API':")
for key in os.environ:
    if 'API' in key.upper():
        value = os.environ[key]
        print(f"  {key}=***скрыто*** (длина: {len(value)})")

# Выбираем API ключ
API_KEY = api_key_from_env or api_key_from_environ

print(f"\nВыбранный API ключ: {API_KEY is not None}")
if API_KEY:
    print(f"Первые 10 символов: {API_KEY[:10]}...")
    print(f"Последние 5 символов: ...{API_KEY[-5:]}")

# Если ключа нет, предлагаем решения
if not API_KEY:
    print("\n=== РЕШЕНИЯ ПРОБЛЕМЫ ===")
    print("1. Создайте файл .env в текущей директории с содержимым:")
    print("   API_KEY=your_actual_api_key_here")
    print("\n2. Или установите переменную окружения:")
    print("   export API_KEY=your_actual_api_key_here")
    print("\n3. Или добавьте в код прямо перед load_dotenv():")
    print("   os.environ['API_KEY'] = 'your_actual_api_key_here'")

    # Интерактивный ввод ключа
    user_input = input("\nХотите ввести API ключ сейчас? (y/n): ")
    if user_input.lower() == 'y':
        API_KEY = input("Введите ваш API ключ: ").strip()
        if API_KEY:
            print("API ключ установлен!")
        else:
            print("Пустой ключ, завершаем работу")
            exit(1)
    else:
        print("Завершаем работу - необходим API ключ")
        exit(1)

# Настройка логгирования
logging.basicConfig(
    filename='tokensgemenh.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

print("\n=== НАЧАЛО ОБРАБОТКИ ===")
API_KEY = API_KEY.strip()
# Проверяем папку с изображениями
images_dir = "enhanced_images"
if not os.path.exists(images_dir):
    print(f"Папка {images_dir} не существует!")
    print("Создайте папку и поместите в неё файлы изображений")
    exit(1)

images = [f for f in os.listdir(images_dir) if f.endswith('.jpg')]
print(f"Найдено изображений: {len(images)}")
print(f"Файлы: {images}")

i = 0
processed_count = 0
while i < 12:
    image_path = f"enhanced_images/счета_page{i}.jpg"

    if not os.path.exists(image_path):
        print(f"Файл {image_path} не найден, пропускаем")
        i += 1
        continue

    print(f"\nОбрабатываем файл: {image_path}")

    try:
        with open(image_path, "rb") as f:
            encode = base64.b64encode(f.read()).decode("utf-8")
            print(f"Файл закодирован в base64 (размер: {len(encode)} символов)")
    except Exception as e:
        print(f"Ошибка чтения файла {image_path}: {e}")
        i += 1
        continue

    base64_image = f"data:image/jpg;base64,{encode}"

    t = {
        "model": "openrouter-gemini-2.5-flash-lite",
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": """Достань 
ИНН
кпп
БИК
Счёт (всегда начинается с 4 кроме случаев оплаты охраны.
тогда он начинается с 0). если он начинается на 3 то это не тот счёт,
найди нажный он точно есть
ИНН покупателя
КПП покупателя
Основание
Назначение платежа (наименование услуг, если дублируется писать 2 раза не нужно, если символов больше 100 сокращай. сразу в этом же поле
после пишется "счёт на оплату № от xx.xxxxxxx.xxxx г )
Всего к оплате
Ставка НДС обязательно в процентах (если нет % посчитай используя сумму к оплате и сумму налога)
, думай внимательно,перепроверяй номера счетов, выведи в формате json чтобы я смог спарсить его в питон. все пункты должны идти в точности друг за другом
это обязательное условие, настрого запрещается менять их местами 
    без каких либо дополнений и ''' , в точности как написано поле двоиточия, не комментируй и не документируй текст,:
    {
      "INN": "ИНН",
      "KPP": "КПП",
      "BIK": "БИК",
      "account": "Счет",
      "INN_recipient": "ИНН покупателя",
      "KPP_recipient": "КПП покупателя",
      "basis": "Основание",
      "goods": "Назначение платежа",
      "total": "Всего к оплате",
      "vat": "Ставка НДС"
    }"""},
                {"type": "image_url", "image_url": {"url": base64_image}}
            ]}
        ]
    }

    try:
        print("Отправляем запрос к API...")
        r = requests.post("https://litellm.poryadok.ru/v1/chat/completions", json=t, headers={"Content-Type": "application/json", "Authorization" : f"Bearer {API_KEY}"})
        print(r)
        print(f"Status code: {r.status_code}")

        if r.status_code == 401:
            print("Ошибка авторизации (401) - проверьте API ключ!")
            print("Возможные причины:")
            print("- Неверный API ключ")
            print("- Истёк срок действия ключа")
            print("- Ключ не имеет доступа к этому API")
            break

        if r.status_code != 200:
            print(f"Ошибка API: {r.status_code}")
            print(f"Response text: {r.text}")
            i += 1
            continue

        js = r.json()
        data = js["choices"][0]["message"]["content"]

        # Извлекаем JSON
        if "```json" in data:
            json_match = re.search(r'```json\s*(.*?)\s*```', data, re.DOTALL)
            if json_match:
                clean_json = json_match.group(1).strip()
            else:
                print("Не удалось извлечь JSON из markdown блока")
                i += 1
                continue
        elif "```" in data:
            json_match = re.search(r'```\s*(.*?)\s*```', data, re.DOTALL)
            if json_match:
                clean_json = json_match.group(1).strip()
            else:
                clean_json = data
        else:
            clean_json = data.strip()

        json_data = json.loads(clean_json)

        print("✅ Данные успешно обработаны:")
        for key, value in json_data.items():
            print(f"  {key}: {value}")

        # Логгирование
        tokens = js.get("usage", {})
        image_filename = f"счета_page{i}.jpg"
        model_name = t.get("model", "unknown")

        log_message = f"Model: {model_name}, Image: {image_filename}, Tokens: {tokens}"
        logging.info(log_message)
        logging.info(f"Response Data: {json_data}")

        processed_count += 1
        print(f"✅ Обработано файлов: {processed_count}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сетевого запроса: {e}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        print(f"Ответ сервера: {r.text if 'r' in locals() else 'Нет ответа'}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")

    i += 1
    print(API_KEY)

print(f"\n=== ЗАВЕРШЕНИЕ ===")
print(f"Всего обработано файлов: {processed_count} из {i}")
print("Проверьте файл tokensgemenh.log для подробной информации")