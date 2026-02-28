from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.password_validation import validate_password


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)
        labels = {'username': 'Введите имя'}
        help_texts = {
            'username': '',
            'password1': '',
            'password2': '',
        }


def clean_password(self):
        password = self.cleaned_data.get('password1')
        validate_password(password, self.instance)

        if password.islower() or password.isupper() or password.isdigit():
            raise forms.ValidationError("Пароль должен содержать буквы различного регистра и цифры")

        return password
