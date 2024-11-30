from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import *
from accounts.utils import image_validator

class foodCategoryForm(forms.ModelForm):
    class Meta:
        model = foodCategory
        fields = ["category_name", "description",]
        

class foodItemForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        vendor_id = kwargs.pop('vendor_id', None)
        category_id = kwargs.pop('category_id', None)

        super(foodItemForm, self).__init__(*args, **kwargs)

        self.fields['category'].queryset = foodCategory.objects.filter(vendor__id=vendor_id)
       
    image=forms.ImageField(widget=forms.FileInput(attrs={"class":"btn-btn-info"}), validators=[image_validator])
    class Meta:
        model = foodItem
        fields = ["image", "food_name", "category", "description", "price", "is_available",]
