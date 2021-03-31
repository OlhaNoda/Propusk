from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, mail_admins
from django.db.models import Count
from django.shortcuts import render, redirect
import qrcode
import pyqrcode
import png
from pyqrcode import QRCode
import uuid
from .forms import *


def gen_codes(request):
    c = Company.objects.get(id=1)
    for i in range(30):
        Code.objects.create(company=c, pub_key=str(uuid.uuid4())[:8], sec_key=str(uuid.uuid4())[:8])


def gen_qrcode(data: str):
   # qr = pyqrcode.create(data)
   # qr = qrcode.make(data)

    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,
                       border=4,
                       )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    return img


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
                    user.save()
                    code.user = user
                    code.save(update_fields=('user',))
                    login(request, code.user)
                    return redirect('fill_propusk')
                login(request, code.user)
                return redirect('show_propusk')
            except ObjectDoesNotExist:
                try:
                    user = User.objects.get(username=data['pub_key'])
                    if check_password(data['sec_key'], user.password):
                        login(request, user)
                        return redirect('company_admin')
                    else:
                        error = 'Неверный пароль'
                except ObjectDoesNotExist:
                    error = 'Неверный логин или пароль'
        else:
            error = 'Форма была неверной'
    form = LoginForm()
    context = {
        'form': form,
        'error': error
    }
    return render(request, 'account/login.html', context)


@login_required
def fill_propusk(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = RegistrationForm(instance=request.user)
    return render(request, 'account/fill_propusk.html', context={'form': form})


@login_required
def show_propusk(request):
    context = {'user': request.user,
               # 'qrcode': gen_qrcode(f'http://127.0.0.1:8000/user_info/{request.user.username}')
               }
    return render(request, 'account/propusk.html', context=context)


@login_required
def company_admin(request):
    # user = request.user
    # company = user.company
    codes = Code.objects.all()
    all_codes_number = Code.objects.count()
    free_codes_number = Code.objects.filter(user_id__isnull=True).count()
    context = {
        'codes': codes,
        'all_codes_number': all_codes_number,
        'free_codes_number': free_codes_number,
        # 'company': company
    }
    return render(request, 'account/company_admin.html', context=context)


def show_user_info(request):
    return render(request, 'account/user_info.html', context={'user': request.user})

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
Ссылка, по которой мы будем отавать информацию о пользователе - ссылка для qr-кода
Модуль генерирования qr кода (когда сохраняется профиль)
Реализовать логин через модель юзера, чек пассворд. Если админ - показываем статистку по свободным кодам и сделеать форму 
о запросе дополнитлеьных кодов.  - в виде письма главному админу
Установить docker, docker-compose (логотип синий кит)
"""
