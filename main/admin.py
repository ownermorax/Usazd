from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin, StackedInline
from unfold.widgets import UnfoldAdminMoneyWidget
from unfold.decorators import action
from main.models import Profile, Reservation
from djmoney.models.fields import MoneyField


class UnfoldUserAdmin(BaseUserAdmin, ModelAdmin):
    """Админ-панель для модели User с интеграцией Unfold.

    Объединяет стандартный UserAdmin с функционалом Unfold для улучшенного интерфейса.
    """
    pass

@admin.register(Reservation)
class ReservationAdmin(ModelAdmin):
    """Админ-панель для модели Reservation.

    Предоставляет интерфейс управления бронированиями с возможностью отмены.
    """
    actions_detail = ['cancel_reservation']
    @action(description="Отменить", attrs={"class": "bg-red-600 text-white"})
    def cancel_reservation(self, request, obj):
        """Отменяет выбранное бронирование.

        :param request: HTTP запрос
        :param obj: Объект бронирования
        """
        obj.status = "cancelled"
        obj.save()
        self.message_user(request, "Бронь отменена", messages.SUCCESS)


class ProfileInline(StackedInline):
    """Встроенная админ-панель для модели Profile.

    Позволяет редактировать профиль пользователя непосредственно на странице пользователя.
    """
    model = Profile
    can_delete = False
    fk_name = 'user'
    formfield_overrides = {
        MoneyField: {'widget': UnfoldAdminMoneyWidget},
    }
    fields = ('name', 'balance')


class ReservationInline(StackedInline):
    """Встроенная админ-панель для модели Reservation.

    Отображает бронирования пользователя на странице пользователя.
    """
    model = Reservation
    extra = 0
    readonly_fields = ('station_in', 'station_out', 'reservation_date', 'place_num', 'train', 'user', 'reservation_id')
    can_delete = True


UnfoldUserAdmin.inlines = (ProfileInline, ReservationInline,)
admin.site.unregister(User)
admin.site.register(User, UnfoldUserAdmin)
