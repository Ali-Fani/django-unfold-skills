# Pattern: User Management

User accounts with avatars, status badges, block/verify actions.

## When
Staff managing end-users: verify/block/delete, reset flows, role assignment.

## Reference implementation

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.urls import reverse_lazy

from unfold.admin import ModelAdmin
from unfold.decorators import action, display
from unfold.enums import ActionVariant
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from .models import UserProfile
from .services import user_block


class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


admin.site.unregister(User)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ["user_heading", "is_active_badge", "date_joined"]
    search_fields = ["email", "first_name", "last_name"]
    inlines = [ProfileInline]

    @display(header=True)
    def user_heading(self, obj):
        return [
            obj.get_full_name() or obj.username,
            obj.email,
            (obj.first_name[:1] + obj.last_name[:1]).upper() or "U",
        ]

    @display(description="Status", ordering="is_active", label={
        True: "success",
        False: "danger",
    })
    def is_active_badge(self, obj):
        return "Active" if obj.is_active else "Blocked"

    actions_detail = ["block_user"]

    @action(description="Block", url_path="block", variant=ActionVariant.DANGER,
            permissions=["block_user"],
            dialog={"title": "Block user",
                    "description": "User loses access immediately. Sessions revoked."})
    def block_user(self, request: HttpRequest, object_id: int):
        user_block(object_id, actor=request.user)          # service: is_active=False + sessions purge + audit
        return reverse_lazy_redirect(object_id)

    def reverse_lazy_redirect(self, object_id):
        from django.shortcuts import redirect
        return redirect(reverse_lazy("admin:auth_user_change", args=[object_id]))

    def has_block_user_permission(self, request: HttpRequest, obj=None):
        return request.user.is_superuser
```

```python
# models.py — avatar [UNFOLD: model properties]
class User(AbstractUser):
    @property
    def avatar_url(self) -> str:
        profile = getattr(self, "profile", None)
        return profile.avatar.url if profile and profile.avatar else ""

    @property
    def avatar_badge_variant(self) -> str | None:
        return "primary" if self.is_staff else None

    @property
    def avatar_badge_count(self) -> str | int | None:
        return None
```

## Rules
- Never expose password hashes/keys in list_display/fieldsets.
- Block action: dialog + permission + session revocation in service.
- Role assignment via Django groups — not ad-hoc booleans scattered on User.
- Self-protection: block action must refuse to disable the acting superuser (`if obj == request.user: error`).

## Related
`unfold-modeladmin` (@display header), `unfold-actions`, `unfold-installation` (auth re-registration), `unfold-security`.
