from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid
from django.forms import ValidationError
from django.utils import timezone
from datetime import timedelta

def default_expiry():
    return timezone.now() + timedelta(days=30)

from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid
from django.forms import ValidationError


LICENSE_TYPES = (
    ('REAL', 'Real'),
    ('DEMO', 'Demo'),
)

class License(models.Model):
    MICRO = 'MICRO'
    MACRO = 'MACRO'
    LICENSE_TYPE_CHOICES = [
        (MICRO, 'Micro'),
        (MACRO, 'Macro'),
    ]

    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    owner = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='licenses')
    login_id = models.CharField(max_length=32)
    broker = models.CharField(max_length=128)
    user_name = models.CharField(max_length=128)
    license_type = models.CharField(max_length=10, choices=LICENSE_TYPE_CHOICES, default=MICRO)
    volume = models.DecimalField(max_digits=5, decimal_places=2, default=0.1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=100.00)
    active = models.BooleanField(default=True)
    from_marketplace = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)  # <-- plus de default automatique
    trading_account = models.CharField(max_length=100, blank=True, null=True)
    days_missed = models.IntegerField(default=0)

    def clean(self):
        if self.license_type == self.MICRO:
            if not (0.1 <= self.volume <= 0.9):
                raise ValidationError('Le volume pour une licence Micro doit être entre 0.1 et 0.9.')
        elif self.license_type == self.MACRO:
            if not (1 <= self.volume <= 100):
                raise ValidationError('Le volume pour une licence Macro doit être entre 1 et 100.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def is_valid(self):
        return self.active and (self.expiry_date is None or self.expiry_date > timezone.now())

    def __str__(self):
        return f"{self.key} - {self.owner.username} - {self.license_type} - Volume: {self.volume}"

# Les autres modèles restent identiques (SellOffer, BuyOffer, LicenseTransaction, CustomUser, Robot)...
# Tu peux garder ce que tu avais, ils n'ont pas besoin d'être modifiés pour cette demande.



class SellOffer(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    login_id = models.CharField(max_length=100)
    license = models.ForeignKey(License, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Ajout volume
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vente licence {self.license.key if self.license else 'N/A'} - {self.price}€"


class BuyOffer(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    login_id = models.CharField(max_length=100)
    email = models.EmailField()
    server = models.CharField(max_length=100)
    license_type = models.CharField(max_length=10, choices=LICENSE_TYPES)
    fullname = models.CharField(max_length=200)
    license = models.ForeignKey(License, on_delete=models.SET_NULL, null=True, blank=True)  # AJOUT
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Achat par {self.fullname} ({self.email}) - {self.license_type}"




class LicenseTransaction(models.Model):
    license = models.ForeignKey(License, on_delete=models.CASCADE)
    buyer = models.ForeignKey('CustomUser', related_name='purchases', on_delete=models.CASCADE)
    seller = models.ForeignKey('CustomUser', related_name='sales', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=10, choices=[('MARKET', 'Marketplace'), ('USER', 'User')])

    def __str__(self):
        return f"Transaction: {self.license.key} vendu par {self.seller.username} à {self.buyer.username} pour {self.price}€"


class CustomUser(AbstractUser):
    is_email_verified = models.BooleanField(default=False)
    email_code = models.CharField(max_length=6, null=True, blank=True)
    seed_phrase_hash = models.CharField(max_length=128, null=True, blank=True)
    otp_secret = models.CharField(max_length=32, null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

from django.db import models

class Robot(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    zip_file = models.FileField(upload_to='robots/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
