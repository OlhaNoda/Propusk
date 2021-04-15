from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import get_template
from django.contrib.auth.hashers import check_password
from django.http import HttpResponse
from django.shortcuts import render, redirect
from account.forms import *
from account.tasks import *
from xhtml2pdf import pisa
from Propusk import settings


@login_required
def company_admin(request):
    user: User = request.user
    all_codes_number = Code.objects.filter(company_id=user.company_id).count()
    free_codes_number = Code.objects.filter(user_id__isnull=True, company_id=user.company_id).count()
    context = {
        'user': user,
        'all_codes_number': all_codes_number,
        'free_codes_number': free_codes_number,
    }
    return render(request, 'account/company_admin/company_admin.html', context=context)


@login_required
def show_free_codes(request):
    admin: User = request.user
    try:
        free_codes = Code.objects.filter(user_id__isnull=True, company_id=admin.company_id)
        context = {'free_codes': free_codes}
        return render(request, 'account/company_admin/show_free_codes.html', context=context)
    except ObjectDoesNotExist:
        message = 'Для організації коди не згенеровано!'
        return render(request, 'account/company_admin/show_free_codes.html', context=message)


@login_required
def register_code_by_admin(request, pub_key):
    try:
        code = Code.objects.get(pub_key=pub_key)
        if not code.user:
            user = User(username=pub_key)
            user.set_password(code.sec_key)
            user.company = code.company
            user.save()
            code.user = user
            code.save(update_fields=('user',))
            request.session['username'] = user.username
            return redirect('register_user_by_admin')
        message = 'Користувача з цими параметрами вже зареєстровано раніше'
        return render(request, 'account/company_admin/show_free_codes.html', context={'message': message})
    except ObjectDoesNotExist:
        message = 'Невірний логін/пароль'
    return render(request, 'account/company_admin/show_free_codes.html', context={'message': message})


@login_required
def register_user_by_admin(request):
    user = User.objects.get(username=request.session.get('username'))
    message = ''
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user.last_name = data['last_name']
            user.first_name = data['first_name']
            user.patronymic = data['patronymic']
            user.birthdate = data['birthdate']
            user.save()
            gen_qrcode(user.username)
            request.session['username'] = user.username
            return redirect('show_transport_pass_by_admin')
        else:
            message = 'Форму заповнено не коректно'
    form = RegistrationForm()
    context = {
        'form': form,
        'message': message
    }
    return render(request, 'account/company_admin/register_user.html', context=context)


@login_required
def show_transport_pass_by_admin(request):
    user = User.objects.get(username=request.session.get('username'))
    request.session['username'] = user.username
    return render(request, 'account/company_admin/show_transport_pass.html', context={'user': user})


@login_required
def export_pdf_by_admin(request):
    user = User.objects.get(username=request.session.get('username'))
    template_path = 'account/user/transport_pass_pdf.html'
    context = {'user': user}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="transport_pass.pdf'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Errors' + html + '</pre>')
    return response


@login_required
def send_email_admin(request):
    message = ''
    user: User = request.user
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                admin_emails = []
                admins = User.objects.filter(is_superuser=True)
                for admin in admins:
                    admin_emails.append(admin.email)
                data = form.cleaned_data
                mail = send_email_task(
                    f'Додаткові ключі для {user.company.name} ({user.company.kod})',
                    data['content'],
                    settings.EMAIL_HOST_USER,
                    admin_emails
                )
                message = 'Лист надіслано!'
                context = {
                    'form': form,
                    'message': message
                }
                return render(request, 'account/company_admin/send_email.html', context=context)
            except ObjectDoesNotExist:
                message = 'Поштову адресу адміністратора не знайдено'
        else:
            message = 'Форму заповнено не коректно'
    form = ContactForm()
    context = {
        'form': form,
        'message': message
    }
    return render(request, 'account/company_admin/send_email.html', context=context)


@login_required
def show_users_info(request):
    admin: User = request.user
    codes = Code.objects.filter(user_id__isnull=False, company=admin.company)
    context = {
        'admin': admin,
        'codes': codes
    }
    return render(request, 'account/company_admin/users_info.html', context=context)


@login_required
def search_user_info(request):
    admin: User = request.user
    message = ''
    if request.method == "POST":
        form = UserSearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            users_list = User.objects.filter(last_name=data['last_name'], company=admin.company)
            codes = Code.objects.filter(user__in=users_list)
            if not codes:
                message = 'Користувачів не знайдено'
            context = {
                'form': form,
                'message': message,
                'codes': codes
            }
            return render(request, 'account/company_admin/search_user_info.html', context=context)
        else:
            message = 'Форму заповнено не коректно'
    form = UserSearchForm()
    context = {
        'form': form,
        'message': message,
    }
    return render(request, 'account/company_admin/search_user_info.html', context=context)


@login_required
def delete_user(request, user_name):
    try:
        user = User.objects.get(username=user_name)
        user.delete()
        message = 'Користувача видалено'
    except ObjectDoesNotExist:
        message = 'Користувача не знайдено'
    form = UserSearchForm()
    context = {
        'form': form,
        'message': message,
    }
    return render(request, 'account/company_admin/search_user_info.html', context=context)


@login_required
def show_user_transport_pass(request, user_name):
    user = User.objects.get(username=user_name)
    return render(request, 'account/company_admin/show_transport_pass.html', context={'user': user})


@login_required
def change_user(request, user_name):
    user = User.objects.get(username=user_name)
    message = ''
    if request.method == "POST":
        form = RegistrationForm(request.POST, instance=user)
        if form.is_valid():
            data = form.cleaned_data
            user.last_name = data['last_name']
            user.first_name = data['first_name']
            user.patronymic = data['patronymic']
            user.birthdate = data['birthdate']
            user.save()
            request.session['username'] = user.username
            return redirect('show_transport_pass_by_admin')
        else:
            message = 'Форму заповнено не коректно'
    form = RegistrationForm(instance=user)
    context = {
        'form': form,
        'message': message,
        'user': user
    }
    return render(request, 'account/company_admin/change_user.html', context=context)


@login_required
def change_admin_password(request):
    message = ''
    user: User = request.user
    if request.method == "POST":
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if check_password(data['old_password'], user.password):
                user.set_password(data['new_password'])
                user.save()
                return redirect('login')
            else:
                message = 'Невірний старий пароль'
        else:
            message = 'Форма заповнена не коректно'
    form = ChangePasswordForm()
    context = {
        'form': form,
        'message': message
    }
    return render(request, 'account/company_admin/change_admin_password.html', context=context)
