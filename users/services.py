import random
import string
from urllib.parse import quote

import requests

from config.settings import DEBUG, SMS_EMAIL, SMS_SIGN, SMS_TOKEN


def generate_invaite_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def send_sms(phone, message):
    try:
        formatted_phone = phone.lstrip("+")
        encoded_text = quote(message)
        encoded_sign = quote(SMS_SIGN)
        if DEBUG:
            print(f"Код {message} будет отправлен на номер {formatted_phone}.")
            return True
        if DEBUG:
            api_sms = "testsend?"
        else:
            api_sms = "send?"

        url = (
            f"https://{SMS_EMAIL}:{SMS_TOKEN}"
            f"@gate.smsaero.ru/v2/sms/{api_sms}"
            f"number={formatted_phone}&"
            f"text={encoded_text}&"
            f"sign={encoded_sign}&"
            f"channel=DIRECT"
        )

        response = requests.get(
            requests.utils.requote_uri(url),
            headers={"Accept": "application/json"},
            timeout=5,
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
