from django.urls import path
from .views import super_admin_views, main_views, company_admin_views, user_views

urlpatterns = [
    path('', main_views.index, name='home'),
    path('login', main_views.login_user, name='login'),
    path('registration', user_views.registration, name='registration'),
    path('propusk', user_views.show_propusk, name='show_propusk'),
    path('transport_pass_pdf', user_views.export_pdf, name='export_pdf'),
    path('user_info/<str:user_name>', user_views.show_user_info, name='user_info'),
    path('company_admin', company_admin_views.company_admin, name='company_admin'),
    path('company_admin/send_email', company_admin_views.send_email_admin, name='send_email_admin'),
    path('company_admin/free_codes', company_admin_views.show_free_codes, name='show_free_codes'),
    path('company_admin/register_user', company_admin_views.register_user_by_admin, name='register_user_by_admin'),
    path('company_admin/transport_pass', company_admin_views.show_transport_pass_by_admin, name='show_transport_pass_by_admin'),
    path('super_admin', super_admin_views.super_admin, name='super_admin'),
    path('super_admin/create_company_admin', super_admin_views.create_company_admin, name='create_company_admin'),
    path('super_admin/company_info', super_admin_views.show_company_info, name='company_info'),
    path('super_admin/generate_codes', super_admin_views.generate_codes, name='generate_codes'),
]
