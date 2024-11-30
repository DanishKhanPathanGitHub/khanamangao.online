from django.contrib import admin
from .models import Vendor, OpeningHours
# Register your models here.
@admin.register(Vendor)
class vendorAadmin(admin.ModelAdmin):
    list_display = ('user', 'vendor_name', 'created_at', 'is_approved',)

@admin.register(OpeningHours)
class openingHoursAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'day', 'from_hour', 'to_hour')