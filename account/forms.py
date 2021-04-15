from .models import *
from django import forms


class LoginForm(forms.ModelForm):
    class Meta:
        model = Code
        fields = ['pub_key', 'sec_key']
        widgets = {
            'sec_key': forms.PasswordInput
        }


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        max_length=8
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        max_length=8
    )


class RegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['patronymic'].widget.attrs.update({'class': 'form-control'})
        self.fields['birthdate'].widget.attrs.update({'class': 'form-control'})

    def clean_birthdate(self):
        val = self.cleaned_data['birthdate']
        print(val, type(val))
        return val

    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'patronymic', 'birthdate']


class ContactForm(forms.Form):
    content = forms.CharField(
        label='Текст',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5})
    )


class CompanySearchForm(forms.Form):
    company_kod = forms.CharField(
        label='ЄДРПОУ',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class UserSearchForm(forms.Form):
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class GenerateCodesForm(forms.Form):
    company_kod = forms.CharField(
        label='ЄДРПОУ',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    codes_number = forms.IntegerField(
        label='Кількість кодів',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )


class RegistrationByAdminForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=8
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        max_length=8
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    patronymic = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=100
    )
    birthdate = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control'}),
    )
