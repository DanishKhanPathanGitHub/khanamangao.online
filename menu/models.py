from django.db import models
from accounts.models import *
from vendor.models import *
# Create your models here.

class foodCategory(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=False)
    description = models.TextField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'catagory'
        verbose_name_plural = 'catagories'

    def clean(self):
        self.category_name = self.category_name.capitalize()

    def __str__(self):
        return self.category_name    

class foodItem(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    category = models.ForeignKey(foodCategory, on_delete=models.CASCADE, related_name='fooditems')
    food_name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=100, unique=False)
    description = models.TextField(max_length=250, blank=True)
    image = models.ImageField(upload_to='foodimages', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.food_name    
    
    def clean(self):
        self.food_name = self.food_name.capitalize()