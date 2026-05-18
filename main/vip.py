import datetime
from .models import Profile


class Vip:
    def __init__(self):
        pass

    def vip_users_count(self):
        return Profile.objects.filter(is_vip=True).count()

    def add_vip_user(self, user_id, duration, price):
        profile = Profile.objects.get(user__id=user_id)
        now = datetime.datetime.now()
        profile.vip_data = now + datetime.timedelta(days=duration)
        profile.is_vip = True
        profile.update_balance(-price)
        profile.save()
        return True
