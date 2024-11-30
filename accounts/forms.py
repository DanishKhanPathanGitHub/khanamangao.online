from django import forms
from .models import *

class userForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ("firstname", "lastname", "username", "email", "phone_no", "password",)

    def clean(self):
        cleaned_data = super(userForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if not password or not confirm_password:
            raise forms.ValidationError("Password must not be empty")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

class userProfileForm(forms.ModelForm):
    address=forms.CharField(widget=forms.TextInput(attrs={"required":"required", "placeholder":"start typing..."}))
    profile_pic=forms.ImageField(widget=forms.FileInput(attrs={"class":"btn-btn-info"}))
    #one way to make field readonly
    latitude=forms.CharField(widget=forms.TextInput(attrs={"readonly":"readonly"}))
    
    class Meta:
        model = userProfile
        fields = ["profile_pic", "address", "country", "state", "city", "pincode","latitude", "longitude",]
    #over-ridding method for making field readonly
    def __init__(self, *args, **kwargs):
        super(userProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field=='longitude':
                self.fields[field].widget.attrs['readonly']='readonly'


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('firstname', 'lastname', 'phone_no')