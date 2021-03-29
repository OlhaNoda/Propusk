from .models import *
from django.forms import ModelForm, TextInput, Textarea


class LoginForm(ModelForm):
    class Meta:
        model = Code
        fields = ['pub_key', 'sec_key']


class RegistrationForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone']
