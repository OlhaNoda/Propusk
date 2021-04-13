from celery import shared_task
from django.core.mail import send_mail
import pyqrcode


@shared_task
def send_email_task(subject: str, content: str, sender: str, recipients: list[str]):
    send_mail(subject, content, sender, recipients, fail_silently=False)


@shared_task
def gen_qrcode(username):
    qr = pyqrcode.create(f'http://127.0.0.1:8000/user_info/{username}')
    file_name = f'media/qr_codes/qr_{username}.png'
    qr.png(file_name, scale=6)
