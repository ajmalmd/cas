from django import forms
from .models import Customer


class CustomerCreateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            "full_name",
            "email",
            "phone",
            "photo",
            "resume",
        ]

    def clean_photo(self):
        photo = self.cleaned_data["photo"]

        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if photo.content_type not in allowed_types:
            raise forms.ValidationError(
                "Upload a JPG, PNG, or WebP image."
            )

        if photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "Photo must be 5 MB or smaller."
            )

        return photo

    def clean_resume(self):
        resume = self.cleaned_data["resume"]

        allowed_types = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]
        if resume.content_type not in allowed_types:
            raise forms.ValidationError(
                "Upload a PDF or Word document."
            )

        if resume.size > 10 * 1024 * 1024:
            raise forms.ValidationError(
                "Resume must be 10 MB or smaller."
            )

        return resume
