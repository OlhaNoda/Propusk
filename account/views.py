from django.shortcuts import render
import uuid
from .models import Company, Code


def gen_codes(request):
    c = Company.objects.get(id=1)
    for i in range(30):
        Code.objects.create(company=c, pub_key=str(uuid.uuid4())[:8], sec_key=str(uuid.uuid4())[:8])
