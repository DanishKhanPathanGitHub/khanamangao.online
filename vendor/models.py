from collections.abc import Iterable
from django.db import models
from accounts.models import User, userProfile
from accounts.utils import send_notification

from django.core.exceptions import ValidationError
from datetime import datetime
# Create your models here.

class Vendor(models.Model):
    user = models.OneToOneField(User, related_name = 'user', on_delete=models.CASCADE)
    vendor_profile = models.OneToOneField(
        userProfile, related_name = 'userProfile', on_delete=models.CASCADE
    )
    vendor_name = models.CharField(max_length=50)
    cover_pic = models.ImageField(upload_to='users/cover_pics', blank=True, null=True)
    slug = models.SlugField(max_length=100, unique=True)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.vendor_name

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if this is a new Vendor

        if is_new:
            super(Vendor, self).save(*args, **kwargs)  # Save the Vendor first
            """# Create OpeningHours for each day if this is a new Vendor
            for day_value, day_name in DAYS:
                OpeningHours.objects.get_or_create(
                    vendor=self,
                    day=day_value,
                    is_closed=True
                )"""
            pass
        else:

            # Check for changes in the is_approved field and send an email if needed
            previous_record = Vendor.objects.get(pk=self.pk)
            if previous_record.is_approved != self.is_approved:
                email_template = 'emails/email_approval_notification.html'
                context = {
                    "user": self.user,
                    "is_approved": self.is_approved,
                }
                if self.is_approved:
                    mail_subject = "Your restaurant has been approved"
                else:
                    mail_subject = "Your restaurant has been suspended"
                
                send_notification(mail_subject, email_template, context)
            super(Vendor, self).save(*args, **kwargs) 


DAYS = [
    (1, ("Monday")),
    (2, ("Tuesday")),
    (3, ("Wednesday")),
    (4, ("Thursday")),
    (5, ("Friday")),
    (6, ("Saturday")),
    (7, ("Sunday"))
]
HOURS_OF_DAY = [
    ('12:00 AM', '12:00 AM'),
    ('01:30 AM', '01:30 AM'),
    ('02:30 AM', '02:30 AM'),
    ('03:30 AM', '03:30 AM'),
    ('04:30 AM', '04:30 AM'),
    ('05:30 AM', '05:30 AM'),
    ('06:30 AM', '06:30 AM'),
    ('07:30 AM', '07:30 AM'),
    ('08:30 AM', '08:30 AM'),
    ('09:30 AM', '09:30 AM'),
    ('10:30 AM', '10:30 AM'),
    ('11:30 AM', '11:30 AM'),
    ('12:30 PM', '12:30 PM'),
    ('01:30 PM', '01:30 PM'),
    ('02:30 PM', '02:30 PM'),
    ('03:30 PM', '03:30 PM'),
    ('04:30 PM', '04:30 PM'),
    ('05:30 PM', '05:30 PM'),
    ('06:30 PM', '06:30 PM'),
    ('07:30 PM', '07:30 PM'),
    ('08:30 PM', '08:30 PM'),
    ('09:30 PM', '09:30 PM'),
    ('10:30 PM', '10:30 PM'),
    ('11:30 PM', '11:30 PM'),
    ('11:59 PM', '11:59 PM'),
]
class OpeningHours(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOURS_OF_DAY, blank=True)
    to_hour = models.CharField(choices=HOURS_OF_DAY, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', 'from_hour')
        unique_together = ('vendor', 'day')

    def __str__(self) -> str:
        return self.get_day_display()
    
    