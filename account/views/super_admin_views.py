from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
import uuid
from account.forms import *


@login_required
def super_admin(request):
    return render(request, 'account/super_admin/super_admin.html')


@login_required
def create_company_admin(request):
    message = ''
    user = ''
    if request.method == "POST":
        form = CompanySearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                login_parameters = {'username': str(uuid.uuid4())[:8], 'password': str(uuid.uuid4())[:8]}
                user = User(username=login_parameters['username'])
                user.set_password(login_parameters['password'])
                user.company = Company.objects.get(kod=data['company_kod'])
                user.company_admin = True
                user.save()
                message = f'Логін: {login_parameters["username"]} Пароль: {login_parameters["password"]}'
            except ObjectDoesNotExist:
                message = 'Організацію не знайдено'
        else:
            message = 'Форма заповнена не коректно'
    form = CompanySearchForm()
    context = {
        'form': form,
        'message': message,
        'user': user
    }
    return render(request, 'account/super_admin/create_company_admin.html', context=context)


@login_required
def show_company_info(request):
    message = ''
    if request.method == "POST":
        form = CompanySearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                search_company = Company.objects.get(kod=data['company_kod'])
                company_admins = User.objects.filter(company=search_company, company_admin=True)
                all_codes_number = Code.objects.filter(company=search_company).count()
                free_codes_number = Code.objects.filter(user_id__isnull=True, company=search_company).count()
                context = {
                    'form': form,
                    'company': search_company,
                    'company_admins': company_admins,
                    'all_codes_number': all_codes_number,
                    'free_codes_number': free_codes_number
                }
                return render(request, 'account/super_admin/company_info.html', context=context)
            except ObjectDoesNotExist:
                message = 'Організацію не знайдено'
        else:
            message = 'Форма заповнена не коректно'
    form = CompanySearchForm()
    context = {
        'form': form,
        'message': message
    }
    return render(request, 'account/super_admin/company_info.html', context=context)


@login_required
def generate_codes(request):
    message = ''
    if request.method == "POST":
        form = GenerateCodesForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                search_company = Company.objects.get(kod=data['company_kod'])
                for i in range(data['codes_number']):
                    Code.objects.create(
                        pub_key=str(uuid.uuid4())[:8],
                        sec_key=str(uuid.uuid4())[:8],
                        company=search_company
                    )
                message = f'Для {search_company.name} ({search_company.kod}) згенеровано {data["codes_number"]} кодів'
            except ObjectDoesNotExist:
                message = 'Організацію не знайдено'
        else:
            message = 'Форма заповнена не коректно'
    form = GenerateCodesForm()
    context = {
        'form': form,
        'message': message
    }
    return render(request, 'account/super_admin/generate_codes.html', context=context)
