# Generated by Django 5.1.5 on 2025-01-27 16:47

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drone', '0019_alter_medication_code_alter_medication_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medication',
            name='code',
            field=models.CharField(max_length=100, validators=[django.core.validators.RegexValidator(message='Invalid Format', regex='^(?=.*[a-zA-Z0-9])[a-zA-Z0-9\\_]+$')]),
        ),
        migrations.AlterField(
            model_name='medication',
            name='name',
            field=models.CharField(max_length=100, validators=[django.core.validators.RegexValidator(message='Invalid Format', regex='^(?=.*[a-zA-Z0-9])[a-zA-Z0-9\\-_]+$')]),
        ),
    ]
