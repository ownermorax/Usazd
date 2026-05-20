import datetime

from .models import Profile


class Vip:
    """Класс для управления VIP статусами пользователей.

    Предоставляет методы для подсчета VIP пользователей и добавления VIP статуса.
    """

    def __init__(self):
        pass

    def vip_users_count(self):
        """Возвращает количество пользователей с VIP статусом.

        :return: Количество VIP пользователей
        :rtype: int
        """
        return Profile.objects.filter(is_vip=True).count()

    def add_vip_user(self, user_id, duration, price):
        """Добавляет VIP статус пользователю.

        :param user_id: ID пользователя
        :param duration: Длительность VIP в днях
        :param price: Стоимость VIP статуса
        :return: True в случае успеха
        :rtype: bool
        """
        profile = Profile.objects.get(user__id=user_id)
        now = datetime.datetime.now()
        profile.vip_data = now + datetime.timedelta(days=duration)
        profile.is_vip = True
        profile.update_balance(-price)
        profile.save()
        return True
