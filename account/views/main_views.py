from django.contrib.auth import login
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from account.forms import *


def index(request):
    return render(request, 'account/home.html')


def login_user(request):
    error = ''
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                if not User.objects.all():
                    user = User(username='superadmin', is_superuser=True)
                    user.set_password('superadmin')
                    user.save()
                else:
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
                    return redirect('user')
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
