# Generated by Django 4.0.4 on 2022-05-31 07:25

import common.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_fsm
import fireblocks.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExternalWallet',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('id', models.TextField(primary_key=True, serialize=False, unique=True)),
                ('name', models.TextField(help_text='Unique name for the wallet')),
                ('customer_ref_id', models.TextField(help_text='The ID for AML providers to associate the owner of funds with transactions')),
            ],
            options={
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='ExternalWalletAsset',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('address', models.TextField(help_text='Asset address. Globally unique per asset')),
                ('status', models.CharField(choices=[('WAITING_FOR_APPROVAL', 'Waiting for approval'), ('APPROVED', 'Approved'), ('CANCELLED', 'Cancelled'), ('REJECTED', 'Rejected'), ('FAILED', 'Failed')], default='WAITING_FOR_APPROVAL', max_length=30)),
                ('tag', models.TextField(help_text='Destination tag of the wallet')),
            ],
            options={
                'verbose_name_plural': 'external wallet assets',
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='FireblocksWallet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='LabelledAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=50, unique=True)),
                ('label', models.TextField(help_text='Description of address')),
            ],
        ),
        migrations.CreateModel(
            name='VaultAccount',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('vault_id', models.TextField(primary_key=True, serialize=False, unique=True)),
                ('name', models.TextField()),
                ('customer_ref_id', models.TextField(help_text='The ID for AML providers to associate the owner of funds with transactions')),
            ],
            options={
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='VaultAsset',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('asset_id', models.TextField(primary_key=True, serialize=False, unique=True)),
                ('is_erc_20', models.BooleanField(default=False, help_text='Is this asset an ERC-20 asset?')),
            ],
            options={
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='VaultWithdrawal',
            fields=[
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=18, max_digits=30, validators=[common.validators.validate_positive])),
                ('status', django_fsm.FSMField(choices=[('new', 'New'), ('approved', 'Approved'), ('queued', 'Queued'), ('sent', 'Sent'), ('confirmed', 'Confirmed'), ('frozen', 'Frozen'), ('cancelled', 'Cancelled'), ('rejected', 'Rejected'), ('failed', 'Failed')], default='new', max_length=30)),
                ('transaction_id', fireblocks.fields.NullTextField(default=None, help_text='The transaction ID of the withdrawal transaction', unique=True)),
                ('wallet_asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fireblocks.externalwalletasset')),
            ],
            options={
                'ordering': ['-created_date'],
                'get_latest_by': ['modified_date', 'created_date'],
            },
        ),
        migrations.CreateModel(
            name='WithdrawalJob',
            fields=[
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('address', models.CharField(help_text='Address to withdraw to', max_length=50)),
                ('amount', models.DecimalField(decimal_places=18, max_digits=30, validators=[common.validators.validate_positive])),
                ('status', django_fsm.FSMField(choices=[('new', 'New'), ('pending', 'Pending'), ('success', 'Success'), ('failed', 'Failed')], default='new', max_length=30)),
                ('error', models.TextField(blank=True, help_text='Error information if the job fails')),
                ('asset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fireblocks.vaultasset')),
                ('withdrawal', models.OneToOneField(blank=True, help_text='The VaultWithdrawal created by this job', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='job', to='fireblocks.vaultwithdrawal')),
            ],
            options={
                'ordering': ['-created_date'],
                'get_latest_by': ['modified_date', 'created_date'],
            },
        ),
        migrations.CreateModel(
            name='VaultWalletAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('address', models.TextField(help_text='Asset address. Globally unique per asset')),
                ('description', models.TextField(help_text='Address description')),
                ('tag', models.TextField(blank=True)),
                ('type', models.TextField(help_text='Address type')),
                ('wallet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fireblocks.fireblockswallet')),
            ],
            options={
                'verbose_name_plural': 'vault wallet addresses',
                'ordering': ['-created_date'],
            },
        ),
        migrations.CreateModel(
            name='VaultDeposit',
            fields=[
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('status', django_fsm.FSMField(choices=[('new', 'New'), ('received', 'Received'), ('confirmed', 'Confirmed')], default='new', max_length=30)),
                ('address', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fireblocks.vaultwalletaddress')),
            ],
            options={
                'ordering': ['-created_date'],
                'get_latest_by': ['modified_date', 'created_date'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True, help_text='Transaction creation date in SS.')),
                ('created_at', models.DateTimeField(editable=False, help_text='Transaction creation date in Fireblocks.')),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('tx_id', models.TextField(primary_key=True, serialize=False, unique=True)),
                ('asset_id', models.TextField()),
                ('data', models.JSONField()),
                ('deposit', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fireblocks.vaultdeposit')),
                ('withdrawal', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='fireblocks.vaultwithdrawal')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='fireblockswallet',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fireblocks.vaultasset'),
        ),
        migrations.AddField(
            model_name='fireblockswallet',
            name='vault_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fireblocks.vaultaccount'),
        ),
        migrations.AddField(
            model_name='externalwalletasset',
            name='asset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fireblocks.vaultasset'),
        ),
        migrations.AddField(
            model_name='externalwalletasset',
            name='wallet',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assets', to='fireblocks.externalwallet'),
        ),
        migrations.AddField(
            model_name='externalwallet',
            name='label',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='fireblocks.labelledaddress'),
        ),
        migrations.AddIndex(
            model_name='vaultwalletaddress',
            index=models.Index(fields=['wallet', 'address'], name='fireblocks__wallet__b1ca6e_idx'),
        ),
        migrations.AddConstraint(
            model_name='vaultwalletaddress',
            constraint=models.UniqueConstraint(fields=('wallet', 'address'), name='unique_address'),
        ),
        migrations.AddConstraint(
            model_name='transaction',
            constraint=models.CheckConstraint(check=models.Q(('deposit__isnull', True), ('withdrawal__isnull', True), _connector='OR'), name='deposit_or_withdrawal'),
        ),
        migrations.AlterUniqueTogether(
            name='fireblockswallet',
            unique_together={('vault_account', 'asset')},
        ),
        migrations.AddIndex(
            model_name='externalwalletasset',
            index=models.Index(fields=['wallet', 'asset', 'address'], name='fireblocks__wallet__dfcbab_idx'),
        ),
        migrations.AddConstraint(
            model_name='externalwalletasset',
            constraint=models.UniqueConstraint(fields=('wallet', 'asset'), name='asset_unique_per_wallet'),
        ),
        migrations.AddConstraint(
            model_name='externalwalletasset',
            constraint=models.UniqueConstraint(fields=('wallet', 'asset', 'address'), name='ewa_unique_address'),
        ),
    ]
