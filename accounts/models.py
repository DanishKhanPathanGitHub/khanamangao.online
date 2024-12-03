from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point
# Create your models here.
class userManager(BaseUserManager):
    def create_user(self, firstname, lastname, username, email, password=None):
        if not email:
            raise ValueError("email required...")
        if not username:
            raise ValueError("username required...")
        user = self.model(
            username = username,
            firstname = firstname,
            lastname = lastname,
            email = self.normalize_email(email)
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, firstname, lastname, username, email, password=None):
        user = self.create_user(
            username = username,
            firstname = firstname,
            lastname = lastname,
            password = password,
            email = self.normalize_email(email)
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user
    
class User(AbstractBaseUser):
    customer = 1
    Vendor = 2
    role_choices = (
        (customer, "customer"),
        (Vendor, "restaurant"),
    )

    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    role = models.PositiveSmallIntegerField(choices=role_choices, default=1)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'firstname', 'lastname']
    objects = userManager()

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
    
class userProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='users/profile_pics', blank=True, null=True)
    address = models.CharField(max_length=300,blank=True, null=True)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)
    location = gismodels.PointField(blank=True, null=True, srid=4326)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username
  
    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude), float(self.latitude))
        return super(userProfile, self).save(*args, **kwargs)
