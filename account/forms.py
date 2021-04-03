from .models import *
from django import forms


class LoginForm(forms.ModelForm):
    class Meta:
        model = Code
        fields = ['pub_key', 'sec_key']
        widgets = {
            'sec_key': forms.PasswordInput
        }


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'phone']


class ContactForm(forms.Form):
    subject = forms.CharField(
        label='Тема',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    content = forms.CharField(
        label='Текст',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )

