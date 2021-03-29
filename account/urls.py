from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('login', views.login, name='login'),
    path('registration', views.registration_user, name='registration_user'),
    path('propusk', views.show_propusk, name='propusk'),
    path('company_admin', views.company_admin, name='company_admin'),
]
