# Generated by Django 3.1.7 on 2021-04-07 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_user_gr_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='gr_code',
        ),
        migrations.AlterField(
            model_name='company',
            name='kod',
            field=models.CharField(max_length=8, unique=True),
        ),
    ]