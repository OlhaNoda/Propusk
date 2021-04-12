
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
from .forms import *
from .tasks import *
from xhtml2pdf import pisa


@login_required
def export_pdf(request):
    user = request.user
    template_path = 'account/user/transport_pass_pdf.html'
    context = {'user': user}
    response = HttpResponse(content_type='application/pdf')
   # response['Content-Disposition'] = 'attachment; filename="transport_pass.pdf'
    response['Content-Disposition'] = 'filename="transport_pass.pdf'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Errors' + html + '</pre>')
    return response


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


@login_required
def registration(request):
    user: User = request.user
    if request.method == "POST":
        form = RegistrationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            if not user.company_admin:
                gen_qrcode(user.username)
                return redirect('show_propusk')
            else:
                return redirect('company_admin')
    else:
        form = RegistrationForm(instance=request.user)
    return render(request, 'account/user/registration.html', context={'form': form})


@login_required
def show_propusk(request):
    return render(request, 'account/user/propusk.html', context={'user': request.user})


def show_user_info(request, user_name):
    user = get_object_or_404(User, username=user_name)
    return render(request, 'account/user/user_info.html', context={'user': user})


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
    return render(request, 'account/company_admin/company_admin.html', context=context)


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
                mail = send_email_task(data['subject'], data['content'], 'super_test1111@ukr.net', admin_emails)
                if mail:
                    messages.success(request, 'Письмо отправлено!')
                    return redirect('send_email_admin')
                else:
                    messages.error(request, 'Ошибка отправки')
            except ObjectDoesNotExist:
                pass
        else:
            messages.error(request, 'Ошибка оправки')
    else:
        form = ContactForm()
    return render(request, 'account/company_admin/send_email.html', {'form': form})


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
            login_parameters = gen_code()
            user = User(username=login_parameters['username'])
            user.set_password(login_parameters['password'])
            user.company = Company.objects.get(kod=data['company_kod'])
            user.company_admin = True
            user.save()
            message = f'Логін: {login_parameters["username"]} Пароль: {login_parameters["password"]}'
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
            search_company = Company.objects.get(kod=data['company_kod'])
            for i in range(data['codes_number']):
                login_parameters = gen_code()
                Code.objects.create(
                    pub_key=login_parameters['username'],
                    sec_key=login_parameters['password'],
                    company=search_company
                )
            message = f'Для {search_company.name} ({search_company.kod}) згенеровано {data["codes_number"]} кодів'
        else:
            message = 'Форма заповнена не коректно'
    form = GenerateCodesForm()
    context = {
        'form': form,
        'message': message
    }
    return render(request, 'account/super_admin/generate_codes.html', context=context)


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
