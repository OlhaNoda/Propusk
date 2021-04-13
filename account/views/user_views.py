from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import get_template
from django.shortcuts import render, redirect, get_object_or_404
from account.forms import *
from account.tasks import *
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
        form = RegistrationForm(instance=user)
    return render(request, 'account/user/registration.html', context={'form': form})


@login_required
def show_propusk(request):
    return render(request, 'account/user/propusk.html', context={'user': request.user})


def show_user_info(request, user_name):
    user = get_object_or_404(User, username=user_name)
    return render(request, 'account/user/user_info.html', context={'user': user})
