# Generated by Django 5.2.3 on 2025-07-02 19:44

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import licenses.models
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_email_verified', models.BooleanField(default=False)),
                ('email_code', models.CharField(blank=True, max_length=6, null=True)),
                ('seed_phrase_hash', models.CharField(blank=True, max_length=128, null=True)),
                ('otp_secret', models.CharField(blank=True, max_length=32, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='customuser_set', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='customuser_set', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='BuyOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_id', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('server', models.CharField(max_length=100)),
                ('license_type', models.CharField(choices=[('REAL', 'Real'), ('DEMO', 'Demo')], max_length=10)),
                ('fullname', models.CharField(max_length=200)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('login_id', models.CharField(max_length=32)),
                ('broker', models.CharField(max_length=128)),
                ('user_name', models.CharField(max_length=128)),
                ('license_type', models.CharField(choices=[('MICRO', 'Micro'), ('MACRO', 'Macro')], default='MICRO', max_length=10)),
                ('volume', models.DecimalField(decimal_places=2, default=0.1, max_digits=5)),
                ('price', models.DecimalField(decimal_places=2, default=100.0, max_digits=10)),
                ('active', models.BooleanField(default=True)),
                ('from_marketplace', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expiry_date', models.DateTimeField(default=licenses.models.default_expiry)),
                ('trading_account', models.CharField(blank=True, max_length=100, null=True)),
                ('days_missed', models.IntegerField(default=0)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='licenses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='LicenseTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_date', models.DateTimeField(auto_now_add=True)),
                ('source', models.CharField(choices=[('MARKET', 'Marketplace'), ('USER', 'User')], max_length=10)),
                ('buyer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='purchases', to=settings.AUTH_USER_MODEL)),
                ('license', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='licenses.license')),
                ('seller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SellOffer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_id', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('license', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='licenses.license')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
