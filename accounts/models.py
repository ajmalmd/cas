from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class UserProfile(models.Model):
    class Role(models.TextChoices):
        MAKER = "MAKER", "Maker"
        CHECKER = "CHECKER", "Checker"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
    )

    assigned_checker = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="assigned_makers",
        limit_choices_to={"role": Role.CHECKER},
    )

    def clean(self):
        if self.role == self.Role.CHECKER and self.assigned_checker:
            raise ValidationError(
                {"assigned_checker": "A Checker cannot be assigned to another Checker."}
            )

        if self.role == self.Role.MAKER and not self.assigned_checker:
            raise ValidationError(
                {"assigned_checker": "Every Maker must have an assigned Checker."}
            )

        if (
            self.assigned_checker
            and self.assigned_checker.role != self.Role.CHECKER
        ):
            raise ValidationError(
                {"assigned_checker": "Select a user with the Checker role."}
            )

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
