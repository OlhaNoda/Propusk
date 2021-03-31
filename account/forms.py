from .models import *
from django.forms import ModelForm, TextInput, Textarea, PasswordInput


class LoginForm(ModelForm):
    class Meta:
        model = Code
        fields = ['pub_key', 'sec_key']
        widgets = {
            'sec_key': PasswordInput
        }


class RegistrationForm(ModelForm):
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'phone']
