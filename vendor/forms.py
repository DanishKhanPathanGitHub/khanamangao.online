from django import forms
from .models import Vendor, OpeningHours
from accounts.utils import image_validator

class vendorForm(forms.ModelForm):
    vendor_license = forms.ImageField(widget=forms.FileInput(attrs={"class":"btn-btn-info"}), validators=[image_validator])
    cover_pic = forms.ImageField(widget=forms.FileInput(attrs={"class":"btn-btn-info"}), validators=[image_validator])
    class Meta:
        model = Vendor
        fields = ("vendor_name", "vendor_license", "cover_pic")

class openingHoursForm(forms.ModelForm):

    class Meta:
        model = OpeningHours
        fields = ('day', 'from_hour', 'to_hour', 'is_closed')
        
    