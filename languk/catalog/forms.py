from django.forms import ModelChoiceField, Select, Textarea, TextInput
from django.utils.translation import gettext_lazy as _

from home.forms import RecaptchaModelForm

from catalog.models import ArtifactPage, ArtifactSubmission, UsageFeedback


def submitter_widgets():
    return {
        "submitter_name": TextInput(
            attrs={"class": "input required", "placeholder": _("Ваше ім'я*")}
        ),
        "submitter_email": TextInput(
            attrs={"class": "input required", "placeholder": _("Ваш e-mail*")}
        ),
    }


class SubmitArtifactForm(RecaptchaModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["artifact_type"].empty_label = _("Тип продукту*")

    class Meta:
        model = ArtifactSubmission
        fields = [
            "artifact_type",
            "name",
            "description",
            "links",
            "license",
            "authors",
            "submitter_name",
            "submitter_email",
        ]

        widgets = {
            "artifact_type": Select(attrs={"class": "required"}),
            "name": TextInput(
                attrs={"class": "input required", "placeholder": _("Назва продукту*")}
            ),
            "description": Textarea(
                attrs={
                    "class": "textarea required",
                    "rows": "6",
                    "placeholder": _("Опис продукту*"),
                }
            ),
            "links": Textarea(
                attrs={
                    "class": "textarea",
                    "rows": "4",
                    "placeholder": _("Посилання (по одному в рядку)"),
                }
            ),
            "license": TextInput(
                attrs={"class": "input", "placeholder": _("Ліцензія")}
            ),
            "authors": TextInput(
                attrs={"class": "input", "placeholder": _("Автори")}
            ),
            **submitter_widgets(),
        }


class UsageFeedbackForm(RecaptchaModelForm):
    artifact = ModelChoiceField(
        queryset=ArtifactPage.objects.live().order_by("title"),
        required=False,
        label=_("Продукт"),
        empty_label=_("Оберіть продукт"),
    )

    class Meta:
        model = UsageFeedback
        fields = [
            "artifact",
            "product_name",
            "how_used",
            "organization",
            "submitter_name",
            "submitter_email",
        ]

        widgets = {
            "product_name": TextInput(
                attrs={
                    "class": "input",
                    "placeholder": _("Продукт (якщо немає у списку)"),
                }
            ),
            "how_used": Textarea(
                attrs={
                    "class": "textarea required",
                    "rows": "6",
                    "placeholder": _("Як і де ви використовуєте продукт?*"),
                }
            ),
            "organization": TextInput(
                attrs={"class": "input", "placeholder": _("Організація/проєкт")}
            ),
            **submitter_widgets(),
        }
