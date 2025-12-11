import base64
import json
import logging
import datetime

import requests

# Настройка логгирования один раз
logging.basicConfig(
    filename='tokensgem.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

i = 0
while i < 12:
    b = "sk-KkPONG8A1lC2Kp_ucS0dgg"
    with open(f"output_images/счета_page{i}.jpg", "rb") as f:
        encode=base64.b64encode(f.read()).decode("utf-8")

    base64_image= f"data:image/jpg;base64,{encode}"
    #не вместится, нужен файл, рекуст http запросы

    t = {"model" : "openai-gpt-5-mini",
         "messages" : [
             {"role": "user", "content": [
                 {"type": "text", "text": """Достань 
    Банк получателя
    БИК
    Счет получателя
    Получатель (Компания, ооо и т.д)
    Покупатель(заказчик)
    Товары(работы,услуги)
    Всего к оплате
    
    Поставщик(исполнитель)
    Основание 
    Ставка ндс
    Всего к оплате
    Сумма ндс
    
    
    Покупатель(заказчик) 
    Всего к оплате, думай внимательно,перепроверяй номера счетов, выведи в формате json 
    без каких либо дополнений и ''' , в точности как написано поле двоиточия:
    {
      "osn_bank_recipient": "Банк получателя",
      "osn_bik": "БИК",
      "osn_recipient_account": Счет получателя",
      "osn_recipient": "Получатель (Компания, ооо и т.д)",
      "osn_customer": "Покупатель(заказчик)",
      "osn_goods_services": "Товары(работы,услуги)",
      "osn_total_payment": "Всего к оплате",
      "rasshifr_supplier": "Поставщик(исполнитель)",
      "rasshifr_basis": "Основание",
      "rasshifr_vat_rate": "Ставка ндс",
      "rasshifr_total_payment": "Всего к оплате",
      "rasshifr_vat_amount": "Сумма ндс",
      "raspred_customer": "Покупатель(заказчик)",
      "raspred_total_payment": "Всего к оплате"
    }"""},
                 {"type": "image_url", "image_url": {"url" : base64_image}}
             ]}
         ]}

    r = requests.post("https://litellm.poryadok.ru/v1/chat/completions", json=t, headers={"Content-Type": "application/json", "Authorization" : "Bearer sk-KkPOFG8A1lC2Kp_ucS0dgg"})

    print(f"Status code: {r.status_code}")
    print(f"Response text: {r.text}")
    print(r)
    if r.status_code != 200:
        print(f"Ошибка API: {r.status_code}")
        i = i + 1
        continue

    try:
        js = r.json()
        data = js["choices"][0]["message"]["content"]





        json_data = json.loads(data)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Ошибка парсинга JSON: {e}")
        print(f"Ответ сервера: {r.text}")
        i = i + 1
        continue
    json_full_data = js
    print(json_data)
    print(json_full_data)

    # логгирование токенов
    tokens = js["usage"]
    image_filename = f"счета_page{i}.jpg"
    model_name = t["model"]

    log_message = f"Model: {model_name}, Image: {image_filename}, Tokens: {tokens}"
    logging.info(log_message)
    logging.info(f"Response Data: {json_data}")
    print(f"Logged: {log_message}")
    
    i = i + 1
