from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from unfold.admin import ModelAdmin, StackedInline
from unfold.widgets import UnfoldAdminMoneyWidget
from unfold.decorators import action
from main.models import Profile, Reservation
from djmoney.models.fields import MoneyField


class UnfoldUserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(Reservation)
class ReservationAdmin(ModelAdmin):
    actions_detail = ["cancel_reservation"]

    @action(description="Отменить", attrs={"class": "bg-red-600 text-white"})
    def cancel_reservation(self, request, obj):
        obj.status = "cancelled"
        obj.save()
        self.message_user(request, "Бронь отменена", messages.SUCCESS)


class ProfileInline(StackedInline):
    model = Profile
    can_delete = False
    fk_name = "user"
    formfield_overrides = {
        MoneyField: {"widget": UnfoldAdminMoneyWidget},
    }
    fields = ("name", "balance")


class ReservationInline(StackedInline):
    model = Reservation
    extra = 0
    readonly_fields = ("station_in", "station_out", "reservation_date", "place_num", "train", "user", "reservation_id")
    can_delete = True


UnfoldUserAdmin.inlines = (
    ProfileInline,
    ReservationInline,
)
admin.site.unregister(User)
admin.site.register(User, UnfoldUserAdmin)
