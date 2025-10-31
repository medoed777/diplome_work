import random
import string

import requests

from config.settings import DEBUG, SMS_EMAIL, SMS_SIGN, SMS_TOKEN


def generate_invaite_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def send_sms(phone, message):
    try:
        formatted_phone = phone.lstrip("+")

        if DEBUG:
            print(f"Сообщение {message} будет отправлено на номер {formatted_phone}.")
            return True

        url = f"https://{SMS_EMAIL}:{SMS_TOKEN}@gate.smsaero.ru/v2/sms/send"
        params = {"number": formatted_phone, "text": message, "sign": SMS_SIGN}

        response = requests.get(
            url, params=params, headers={"Accept": "application/json"}, timeout=5
        )

        if response.status_code == 200:
            result = response.json()
            return result.get("success", False)
        else:
            print(f"Ошибка при отправке SMS: {response.status_code} - {response.text}")
        return False

    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети: {e}")
        return False
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return False
