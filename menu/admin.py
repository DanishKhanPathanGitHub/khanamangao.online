from django.contrib import admin
from .models import *
# Register your models here.

class foodCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('category_name',)}
    list_display = ('category_name', 'vendor', 'updated_at')
    search_fields = ('category_name', 'vendor__vendor_name')


class foodItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('food_name',)}
    list_display = ('food_name','category', 'vendor', 'price', 'is_available', 'updated_at',)
    search_fields = ('food_name','category__category_name', 'vendor__vendor_name',)
    list_filter = ('is_available','price',)    

admin.site.register(foodCategory, foodCategoryAdmin)
admin.site.register(foodItem, foodItemAdmin)