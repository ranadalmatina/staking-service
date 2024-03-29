# Generated by Django 4.0.4 on 2022-06-09 23:43

from django.db import migrations, models

import common.validators


class Migration(migrations.Migration):

    dependencies = [
        ('avalanche', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='atomictx',
            options={'ordering': ['-created_date']},
        ),
        migrations.AlterField(
            model_name='atomictx',
            name='amount',
            field=models.DecimalField(decimal_places=18, help_text='Amount in AVAX', max_digits=30, validators=[common.validators.validate_positive]),
        ),
    ]
