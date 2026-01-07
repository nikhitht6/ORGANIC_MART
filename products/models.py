from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    CATEGORY_CHOICES = (
        ('Vegetables', 'Vegetables'),
        ('Fruits', 'Fruits'),
        ('Grains', 'Grains'),
        ('Dairy', 'Dairy'),
    )

    UNIT_CHOICES = (
        ('kg', 'Kilogram'),
        ('unit', 'Unit'),
    )

    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.DecimalField(max_digits=6, decimal_places=2)
    unit = models.CharField(max_length=10,choices=UNIT_CHOICES,default='unit')
    harvest_date = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    # Auto-detect unit based on category
    def save(self, *args, **kwargs):
        if self.category in ['Vegetables', 'Fruits', 'Grains']:
            self.unit = 'kg'
        else:
            self.unit = 'unit'
        super().save(*args, **kwargs)


