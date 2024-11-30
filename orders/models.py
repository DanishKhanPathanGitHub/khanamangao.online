from django.db import models
import simplejson
from accounts.models import User, userProfile
from menu.models import foodItem

# Create your models here.
class Payment(models.Model):
    PAYMENT_METHOD = (
        ('RazorPay', 'RazorPay'),
        ('PayPal', 'PayPal'),
    )
    PAYMENT_STATUS =  (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=50, unique=True)
    payment_method = models.CharField(choices=PAYMENT_METHOD, max_length=15)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=15, choices=PAYMENT_STATUS, default="Pending") 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.transaction_id
    
class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, related_name='order', blank=True, null=True)
    order_number = models.CharField(max_length=25, unique=True)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField(max_length=254)
    address = models.CharField(max_length=200)
    country = models.CharField(max_length=25, blank=True)
    state = models.CharField(max_length=25, blank=True)
    city = models.CharField(max_length=30)
    pincode = models.CharField(max_length=12)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    tax_data = models.JSONField(blank=True, help_text="Data format: {'tax_type':{'tax_percentage':'tax_amount'}}")
    total_tax = models.DecimalField(max_digits=8, decimal_places=2)
    vendor_data = models.JSONField(blank=True, null=True, help_text="Data format: {'vendor_id': {'subtotal': subtotal, 'tax_total': tax_total, 'total': total, 'tax_dict': {'tax_type': {'tax_percentage': percentage, 'tax_amount': amount}}}}")
    status = models.CharField(max_length=15, choices=STATUS, default='New')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def name(self):
        return f'{self.firstname} {self.lastname}'
    
    def get_vendor_data(self, vendor):
        vendor_data = simplejson.loads(self.vendor_data).get(str(vendor.id), None)
        order_info = {
            'order_number': self.order_number,
            'status': self.status,
            'date': self.created_at,
            'subtotal': vendor_data['subtotal'],
            'tax_total': vendor_data['tax_total'],
            'total': vendor_data['total'],
            'tax_breakdown': vendor_data['tax_dict'],
        }

    
    def __str__(self):
        return self.order_number
    
class OrderedFood(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fooditem = models.ForeignKey(foodItem, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.fooditem.food_name
    
    
    