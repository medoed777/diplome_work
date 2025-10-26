import random
import string
from config.settings import SMS_EMAIL, SMS_TOKEN, SMS_SIGN


def generate_invaite_code():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


# def send_sms(phone, message):
#     try:
#         formatted_phone = phone.lstrip("+")
#
#         url = f"https://{SMS_EMAIL}:{SMS_TOKEN}@gate.smsaero.ru/v2/sms/send?number={formatted_phone}&text={message}&sign={SMS_SIGN}"
#
#         logger.debug("Отправка запроса к SMS Aero API")
#         response = requests.get(
#             requests.utils.requote_uri(url),
#             headers={"Accept": "application/json"},
#             timeout=5,
#         )
#
#         if response.status_code == 200:
#             result = response.json()
#             success = result.get("success", False)
#             if success:
#                 logger.info("SMS успешно отправлено")
#                 return True
#             else:
#                 logger.error(f"Ошибка от SMS Aero API: {result}")
#                 return False
#
#         logger.error(f"Ошибка HTTP: {response.status_code} - {response.text}")
#         return False
#
#     except Exception as e:
#         logger.error(f"Неожиданная ошибка при отправке SMS: {str(e)}")
#         return False