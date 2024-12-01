import os
from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food.settings')
import django
django.setup()

from accounts.models import User, userProfile
from vendor.models import Vendor, OpeningHours
from marketplace.models import Tax, Cart
from menu.models import foodCategory, foodItem
from orders.models import Order, OrderedFood, Payment
from django.contrib.auth.models import Group


# Utility function to safely delete data
def delete_if_exists(model, **kwargs):
    """Delete the object if it exists in the database."""
    try:
        obj = model.objects.get(**kwargs)
        obj.delete()
    except ObjectDoesNotExist:
        pass  # If the object does not exist, do nothing


# Delete all data
def delete_all_data():
    # Delete all Cart objects
    Cart.objects.all().delete()

    # Delete all OpeningHours
    OpeningHours.objects.all().delete()

    # Delete all foodItems and foodCategories
    foodItem.objects.all().delete()
    foodCategory.objects.all().delete()

    # Delete all Vendors
    Vendor.objects.all().delete()

    # Delete all userProfiles
    userProfile.objects.all().delete()

    # Delete all Users (Customers and Vendors)
    User.objects.all().delete()

    # Delete all Tax entries
    Tax.objects.all().delete()

    Order.objects.all().delete()

    OrderedFood.objects.all().delete()

    Payment.objects.all().delete()

    print("All data deleted successfully!")


# Main execution
if __name__ == "__main__":
    delete_all_data()
