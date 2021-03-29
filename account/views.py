from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
import uuid
from .forms import *


def gen_codes(request):
    c = Company.objects.get(id=1)
    for i in range(30):
        Code.objects.create(company=c, pub_key=str(uuid.uuid4())[:8], sec_key=str(uuid.uuid4())[:8])


def show_propusk(request):
    return render(request, 'account/propusk.html')


def login(request):
    error = ''
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                code = Code.objects.get(pub_key=data['pub_key'], sec_key=data['sec_key'])
                if code.user:
                    return redirect('company_admin')
                request.session['username'] = code.pub_key
                request.session['password'] = code.sec_key
                return redirect('registration_user')
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


def registration_user(request):
    error = ''
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data['phone'],
                password=request.session['password'],
                username=request.session['username'],
            #    is_staff=1
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


def company_admin(request):
    return render(request, 'account/company_admin.html')


def index(request):
    return render(request, 'account/home.html')


