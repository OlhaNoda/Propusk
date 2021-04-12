from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('login', views.login_user, name='login'),
    path('registration', views.registration, name='registration'),
    path('propusk', views.show_propusk, name='show_propusk'),
    path('transport_pass_pdf', views.export_pdf, name='export_pdf'),
    path('user_info/<str:user_name>', views.show_user_info, name='user_info'),
    path('company_admin', views.company_admin, name='company_admin'),
    path('company_admin/send_email', views.send_email_admin, name='send_email_admin'),
    path('super_admin', views.super_admin, name='super_admin'),
    path('super_admin/create_company_admin', views.create_company_admin, name='create_company_admin'),
    path('super_admin/company_info', views.show_company_info, name='company_info'),
    path('super_admin/generate_codes', views.generate_codes, name='generate_codes'),
]
