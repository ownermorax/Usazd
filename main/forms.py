from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import Reservation

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

class NeuralNetworkForm(forms.Form):
    text = forms.CharField(
        max_length=100,
        label='Введите запрос',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-dark text-bg-dark',
            'placeholder': 'Поиск...',
            'type': 'search'
        })
    )
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['train', 'place_num', 'station_in', 'station_out', 'repeat_type', 'repeat_end_date']
        widgets = {
            'repeat_end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        labels = {
            'train': 'Поезд',
            'place_num': 'Номер места',
            'station_in': 'Станция отправления',
            'station_out': 'Станция назначения',
            'repeat_type': 'Повторять',
            'repeat_end_date': 'Дата окончания повторения',
        }