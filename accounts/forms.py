from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.core.exceptions import ValidationError

from .models import CustomUser


class AdminCustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


class AdminCustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")


class AddUserModelForm(forms.ModelForm):
    password1 = forms.CharField(max_length=128, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=128, widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username']
        labels = {'first_name': 'imie'}

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise ValidationError('hasła nie są takie same')
        return cleaned_data
