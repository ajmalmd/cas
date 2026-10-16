from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import UserProfile

User = get_user_model()


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0
    max_num = 1
    can_delete = False
    fields = ("role", "assigned_checker")


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        "username",
        "email",
        "is_staff",
        "is_active",
    )
    search_fields = ("username", "email")
    list_filter = ("is_staff", "is_active")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "assigned_checker")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email")
    list_select_related = ("user", "assigned_checker")
