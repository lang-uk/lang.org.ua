from django.contrib import admin, messages

from catalog.models import ArtifactSubmission, SectionPage, UsageFeedback
from catalog.utils import create_artifact_draft


@admin.register(ArtifactSubmission)
class ArtifactSubmissionAdmin(admin.ModelAdmin):
    list_display = ["name", "artifact_type", "submitter_name", "added", "processed"]
    list_filter = ["artifact_type", "processed"]
    actions = ["create_draft_pages"]

    def has_add_permission(self, request):
        return False

    @admin.action(description="Створити чернетку продукту з заявки")
    def create_draft_pages(self, request, queryset):
        sections = {
            section.artifact_type_id: section
            for section in SectionPage.objects.filter(artifact_type__isnull=False)
        }
        created = 0
        for submission in queryset.filter(processed=False):
            section = sections.get(submission.artifact_type_id)
            if section is None:
                self.message_user(
                    request,
                    f"Немає розділу для типу «{submission.artifact_type}» — "
                    f"пропущено «{submission.name}»",
                    level=messages.WARNING,
                )
                continue

            artifact = create_artifact_draft(
                section,
                title=submission.name,
                artifact_type=submission.artifact_type,
                short_description=submission.description[:300],
                body=f"<p>{submission.description}</p>",
                authors=submission.authors,
                license=submission.license,
                links=[url.strip() for url in submission.links.splitlines() if url.strip()],
            )
            if artifact is None:
                self.message_user(
                    request,
                    f"Не вдалося створити слаг або сторінка вже існує — "
                    f"пропущено «{submission.name}»",
                    level=messages.WARNING,
                )
                continue

            submission.processed = True
            submission.save(update_fields=["processed"])
            created += 1

        if created:
            self.message_user(
                request, f"Створено чернеток: {created} (див. розділи каталогу в CMS)"
            )


@admin.register(UsageFeedback)
class UsageFeedbackAdmin(admin.ModelAdmin):
    list_display = [
        "__str__",
        "artifact",
        "organization",
        "submitter_email",
        "added",
    ]
    list_filter = ["artifact"]

    def has_add_permission(self, request):
        return False
