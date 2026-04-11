from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin, StackedInline
from unfold.widgets import UnfoldAdminMoneyWidget
from .models import Profile
from djmoney.models.fields import MoneyField

class UnfoldUserAdmin(BaseUserAdmin, ModelAdmin):
    pass

class ProfileInline(StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль и валюта'
    fk_name = 'user'
    formfield_overrides = {
        MoneyField: {'widget': UnfoldAdminMoneyWidget},
    }
    fields = ('name', 'role', 'description', 'avatar', 'balance')

UnfoldUserAdmin.inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UnfoldUserAdmin)
