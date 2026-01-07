from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('FARMER', 'Farmer'),
        ('CUSTOMER', 'Customer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CUSTOMER'
    )

    
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    # ADMIN CONTROL FEATURES
    is_blocked = models.BooleanField(default=False)
    is_verified = models.BooleanField(
        default=False,
        help_text="Used only for FARMER verification"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"
