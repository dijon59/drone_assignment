# Generated by Django 5.1.5 on 2025-01-25 19:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drone', '0002_alter_drone_weight_limit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drone',
            name='weight_limit',
            field=models.DecimalField(decimal_places=1, default=0.0, max_digits=10, validators=[django.core.validators.MaxValueValidator(500.0)]),
        ),
    ]
