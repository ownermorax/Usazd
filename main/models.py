from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    """Модель профиля"""
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    def __str__(self):
        return self.user.username