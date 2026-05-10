from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin, StackedInline
from unfold.widgets import UnfoldAdminMoneyWidget
from .models import Profile
from djmoney.models.fields import MoneyField

class UnfoldUserAdmin(BaseUserAdmin, ModelAdmin):
    """Класс админа для управления пользователями

    Наследует стандартный BaseUserAdmin и ModelAdmin
    от Unfold, добавляя профиль пользователя как Inline-форму"""
    pass

class ProfileInline(StackedInline):
    """Inline-форма для редактирования пользователя
    внутри страницы пользователя.

    Позволяет редактировать профиль и баланс пользователя
    на странице редактирования пользователя.

    :var model: Связанная модель Profile
    :var can_delete: Запрещает удаление пользователя
    :var verbose_name_plural: Отображаемое название
    :var fk_name: Внешний ключ для связи с пользователем
    :var formfield_overrides: Переопределение виджета для MoneyField
    :var fields: Отображаемые поля профиля (имя, роль, описание, аватар, баланс)"""
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
