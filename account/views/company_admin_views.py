from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import get_template
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from account.forms import *
from account.tasks import *
from xhtml2pdf import pisa


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
def register_user_by_admin(request):
    admin: User = request.user
    message = ''
    if request.method == "POST":
        form = RegistrationByAdminForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                code = Code.objects.get(pub_key=data['username'], sec_key=data['password'], company=admin.company)
                if not code.user:
                    user = User(username=code.pub_key)
                    user.set_password(code.sec_key)
                    user.company = code.company
                    user.last_name = data['last_name']
                    user.first_name = data['first_name']
                    user.patronymic = data['patronymic']
                    user.birthdate = data['birthdate']
                    user.save()
                    code.user = user
                    code.save(update_fields=('user',))
                    gen_qrcode(user.username)
                    request.session['username'] = user.username
                    return redirect('show_transport_pass_by_admin')
                message = 'Користувача з цими параметрами вже зареєстровано раніше'
                context = {
                    'form': form,
                    'message': message
                }
                return render(request, 'account/company_admin/register_user.html', context=context)
            except ObjectDoesNotExist:
                message = 'Невірний логін/пароль'
        else:
            message = 'Форму заповнено не коректно'
    form = RegistrationByAdminForm()
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
def export_pdf(request):
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
