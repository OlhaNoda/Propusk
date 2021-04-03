from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.core.mail import send_mail, mail_admins
from django.shortcuts import render, redirect, get_object_or_404
import uuid
from .forms import *
from .tasks import *


def gen_codes(request):
    c = Company.objects.get(id=2)
    for i in range(30):
        Code.objects.create(company=c, pub_key=str(uuid.uuid4())[:8], sec_key=str(uuid.uuid4())[:8])


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
                    return redirect('fill_propusk')
                login(request, code.user)
                return redirect('show_propusk')
            except ObjectDoesNotExist:
                try:
                    user = User.objects.get(username=data['pub_key'])
                    if check_password(data['sec_key'], user.password):
                        login(request, user)
                        if user.company_admin:
                            return redirect('company_admin')
                        else:
                            return redirect('show_propusk')
                    else:
                        error = f"Неверный пароль"
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
    user: User = request.user
    if request.method == "POST":
        form = RegistrationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            gen_qrcode(user.username)
    else:
        form = RegistrationForm(instance=request.user)
    return render(request, 'account/fill_propusk.html', context={'form': form})


@login_required
def show_propusk(request):
    return render(request, 'account/propusk.html', context={'user': request.user})


def show_user_info(request, user_name):
    user = get_object_or_404(User, username=user_name)
    return render(request, 'account/user_info.html', context={'user': user})


@login_required
def company_admin(request):
    user: User = request.user
    codes = Code.objects.all()
    all_codes_number = Code.objects.filter(company_id=user.company_id).count()
    free_codes_number = Code.objects.filter(user_id__isnull=True, company_id=user.company_id).count()
    context = {
        'codes': codes,
        'user': user,
        'all_codes_number': all_codes_number,
        'free_codes_number': free_codes_number,
    }
    return render(request, 'account/company_admin.html', context=context)


@login_required
def send_email_admin(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                admin_emails = []
                admins = User.objects.filter(is_superuser=True)
                for admin in admins:
                    admin_emails.append(admin.email)
                data = form.cleaned_data
                send_email_task(data['subject'], data['content'], request.user.email, admin_emails)
                messages.success(request, 'Письмо отправлено!')
                return redirect('send_email_admin')
            except ObjectDoesNotExist:
                pass
        else:
            messages.error(request, 'Ошибка регистрации')
    else:
        form = ContactForm()
    return render(request, 'account/send_email.html')

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
