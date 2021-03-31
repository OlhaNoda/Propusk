from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('login', views.login_user, name='login'),
    path('fill_propusk', views.fill_propusk, name='fill_propusk'),
    path('propusk', views.show_propusk, name='show_propusk'),
    path('user_info', views.show_user_info, name='user_info'),
    path('company_admin', views.company_admin, name='company_admin'),
]
