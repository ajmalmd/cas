from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "uploaded_by",
        "status",
        "reviewed_by",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "phone")
    list_select_related = ("uploaded_by", "reviewed_by")
    ordering = ("-created_at",)
    readonly_fields = (
        "uploaded_by",
        "status",
        "reviewed_by",
        "reviewed_at",
        "created_at",
        "updated_at",
    )
