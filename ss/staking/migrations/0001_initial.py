# Generated by Django 4.0.4 on 2022-06-09 23:43

import uuid

import django_fsm

from django.db import migrations, models

import common.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FillJob',
            fields=[
                ('status', django_fsm.FSMField(choices=[('new', 'New'), ('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='new', max_length=30)),
                ('created_date', models.DateTimeField(auto_now_add=True, help_text='Transaction creation date in SS.')),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=18, help_text='Amount in AVAX', max_digits=30, validators=[common.validators.validate_positive])),
                ('fireblocks_transaction_id', models.UUIDField(help_text='Fireblocks transaction ID.', null=True)),
            ],
        ),
    ]