import re

from django import forms


class CodeForm(forms.Form):
    code = forms.CharField(max_length=4, label="Код")


class PhoneLoginForm(forms.Form):
    """Форма для входа по номеру телефона"""

    phone = forms.CharField(
        label="Номер телефона",
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "type": "tel",
                "class": "form-control form-control-lg",
                "placeholder": "+7 (999)-999-99-99",
                "id": "phone",
            }
        ),
        error_messages={
            'required': "Это поле обязательно для заполнения.",
            'max_length': "Длина номера не должна превышать 20 символов.",
        }
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].help_text = (
            '- Номер должен начинаться с символа "+"<br>'
            '- Длина номера не должна превышать 20 символов (включая "+")'
            '- Исключите все специальные символы (скобки, тире, пробелы)'
        )

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        cleaned_phone = "".join(char for char in phone if char.isdigit() or char == "+")
        if not cleaned_phone.startswith("+"):
            raise forms.ValidationError("Номер телефона должен начинаться с '+'")
        if len(cleaned_phone) > 20:
            raise forms.ValidationError(
                "Номер телефона не должен превышать 20 символов"
            )
        if not re.match(r"^\+7\d{10}$", cleaned_phone):
            raise forms.ValidationError(
                "Номер телефона должен быть в формате +7XXXXXXXXXX"
            )
        return cleaned_phone
