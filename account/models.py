from django.db import models
from django.contrib.auth.models import AbstractUser


class Company(models.Model):
    name = models.CharField(max_length=255)
    kod = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    patronymic = models.CharField(max_length=100)
    birthdate = models.DateField(null=True)
    phone = models.CharField(max_length=50)
    company_admin = models.BooleanField(default=False)
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.CASCADE)


class Code(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    pub_key = models.CharField(max_length=8)  # логин сотрудника
    sec_key = models.CharField(max_length=8)  # пароль сотрудника
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)


