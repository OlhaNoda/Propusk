from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *


class CompanyAdmin(admin.ModelAdmin):
    prepopulated_fields = {'kod': ('name',)}


admin.site.register(User, UserAdmin)
admin.site.register(Company, CompanyAdmin)
