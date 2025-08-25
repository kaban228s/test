import base64
import json
import logging
import os
import re
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
# Настройка логгирования один раз
logging.basicConfig(
    filename='tokensgemenh.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

load_dotenv()

API_KEY = os.getenv('API_KEY')

folder = Path("enhanced_images")
files = sorted(folder.glob("*.jpg"))

for i, file in enumerate(files, start=1):
    print(API_KEY)
    if not API_KEY:
        print("Ошибка: переменная окружения API_KEY не установлена")
        break

    with open(file, "rb") as f:
        encode = base64.b64encode(f.read()).decode("utf-8")

    base64_image = f"data:image/jpg;base64,{encode}"

    t = {"model": "openrouter-gemini-2.5-flash-lite",
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
      "vat": "Ставка НДС",
    }"""},
                 {"type": "image_url", "image_url": {"url": base64_image}}
             ]}
         ]}

    r = requests.post("https://litellm.poryadok.ru/v1/chat/completions", json=t,
                      headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"})

    print(f"Status code: {r.status_code}")
    print(f"Response text: {r.text}")
    if r.status_code != 200:
        print(f"Ошибка API: {r.status_code}")
        i = i + 1
        continue

    try:
        js = r.json()
        data = js["choices"][0]["message"]["content"]

        if "```json" in data:
            json_match = re.search(r'```json\s*(.*?)\s*```', data, re.DOTALL)
            if json_match:
                clean_json = json_match.group(1).strip()
            else:
                print("Не удалось извлечь JSON из markdown блока")
                i = i + 1
                continue
        elif "```" in data:
            # Если блок кода без указания языка
            json_match = re.search(r'```\s*(.*?)\s*```', data, re.DOTALL)
            if json_match:
                clean_json = json_match.group(1).strip()
            else:
                clean_json = data
        else:
            # Если нет блоков кода, берем как есть
            clean_json = data.strip()

        # Парсим очищенный JSON
        json_data = json.loads(clean_json)

    except (json.JSONDecodeError, KeyError) as e:
        print(f"Ошибка парсинга JSON: {e}")
        print(f"Ответ сервера: {r.text}")
        i = i + 1
        continue

    json_full_data = js
    print("Распарсенные данные:")
    print(json_data)

    tokens = js.get("usage", {})
    image_filename = file.name
    model_name = t.get("model", "unknown")

    log_message = f"Model: {model_name}, Image: {image_filename}, Tokens: {tokens}"
    logging.info(log_message)
    logging.info(f"Response Data: {json_data}")
    print(f"Logged: {log_message}")

    i = i + 1
