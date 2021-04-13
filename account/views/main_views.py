
from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.mail import send_mail, mail_admins
from django.shortcuts import render, redirect, get_object_or_404
import uuid
from account.forms import *
from account.tasks import *
from xhtml2pdf import pisa





def index(request):
    return render(request, 'account/home.html')


def login_user(request):
    error = ''
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                code = Code.objects.get(pub_key=data['pub_key'], sec_key=data['sec_key'])
                if not code.user:
                    user = User(username=code.pub_key)
                    user.set_password(code.sec_key)
                    user.company = code.company
                    user.save()
                    code.user = user
                    code.save(update_fields=('user',))
                    login(request, code.user)
                    return redirect('registration')
                login(request, code.user)
                return redirect('show_propusk')
            except ObjectDoesNotExist:
                try:
                    user = User.objects.get(username=data['pub_key'])
                    if check_password(data['sec_key'], user.password):
                        login(request, user)
                        if user.company_admin:
                            if user.last_name:
                                return redirect('company_admin')
                            else:
                                return redirect('registration')
                        elif user.is_superuser:
                            return redirect('super_admin')
                        else:
                            error = f"Роль користувача не визначено"
                    else:
                        error = f"Невірний пароль"
                except ObjectDoesNotExist:
                    error = 'Невірний логін/пароль'
        else:
            error = 'Форму заповнено не коректно'
    form = LoginForm()
    context = {
        'form': form,
        'error': error
    }
    return render(request, 'account/login.html', context)




"""
def registration_user(request):
    error = ''
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone=data['phone'],
                password=request.session['password'],
                username=request.session['username'],
            )
            code = Code.objects.get(pub_key=user.username, sec_key=user.password)
            code.user = user
            code.save()
            return redirect('propusk')
        else:
            error = 'Форма была неверной'
    form = RegistrationForm()
    context = {
        'form': form,
        'error': error
    }
    return render(request, 'account/registration_propusk.html', context)
"""



"""
сделеать форму о запросе дополнитлеьных кодов.  - в виде письма главному админу
Установить docker, docker-compose (логотип синий кит)
"""
