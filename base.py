import base64
import json
import logging
import datetime

import requests

# Настройка логгирования
logging.basicConfig(
    filename='tokens.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
b = "sk-KkPONG8A1lC2Kp_ucS0dgg"
with open("output_images/счета_page11.jpg", "rb") as f:
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
Всего к оплате, думай внимательно,перепроверяй номера счетов, выведи в формате json:
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

js=(r.json())
data = js["choices"][0]["message"]["content"]
json_data = json.loads(data)
json_full_data = js
print(json_data)
print(json_full_data)

# логгирование токенов
tokens = js["usage"]
i = 1



image_filename = f"счета_page{i}.jpg"
i = i+1
model_name = t["model"]

log_message = f"Model: {model_name}, Image: {image_filename}, Tokens: {tokens}"
logging.info(log_message)
logging.info(f"Response Data: {json_data}")
print(f"Logged: {log_message}")
