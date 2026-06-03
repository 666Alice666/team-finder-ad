from django import forms

from common.forms import validate_github_url

from .models import Project


PROJECT_DESCRIPTION_TEXTAREA_ROWS = 6


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": PROJECT_DESCRIPTION_TEXTAREA_ROWS}),
            "status": forms.Select(
                choices=(
                    (Project.OPEN, "Открыт"),
                    (Project.CLOSED, "Закрыт"),
                )
            ),
        }

    def clean_github_url(self):
        value = self.cleaned_data.get("github_url")
        validate_github_url(value)
        return value

