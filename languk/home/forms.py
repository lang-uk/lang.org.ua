from django.forms import ModelForm, Textarea, TextInput, EmailField

from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

from django.utils.translation import gettext_lazy as _
from home.models import ContactUsMessage


class ContactUsForm(ModelForm):
    required_css_class = "required"

    captcha = ReCaptchaField(widget=ReCaptchaV3)

    class Meta:
        model = ContactUsMessage
        fields = ["author", "text", "email", "phone"]

        widgets = {
            "author": TextInput(
                attrs={
                    "placeholder": _("Ім'я*"),
                    "class": "input__item",
                }
            ),
            "phone": TextInput(
                attrs={
                    "class": "input__item",
                    "placeholder": _("Телефон"),
                }
            ),
            "email": TextInput(
                attrs={
                    "class": "input__item required",
                    "required": "",
                    "placeholder": _("Email*"),
                }
            ),
            "text": Textarea(
                attrs={
                    "required": "",
                    "rows": "6",
                    "class": "input__item-area required",
                    "placeholder": _("Ваше повідомлення"),
                }
            ),
        }
