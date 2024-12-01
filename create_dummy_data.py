import os
import random
import string
from decimal import Decimal
from django.utils.text import slugify
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
from django.core.files.base import ContentFile

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food.settings')
import django

django.setup()

from accounts.models import *
from vendor.models import (
     Vendor, OpeningHours, DAYS
)
from marketplace.models import Tax, Cart
from menu.models import foodCategory, foodItem

# Constants
LOCATIONS = {
    "Gujarat": [
        {"city": "Ahmedabad", "pincode": "380001", "lat": 23.0225, "long": 72.5714, "address": "Ellis Bridge"},
        {"city": "Ahmedabad", "pincode": "380015", "lat": 23.0301, "long": 72.5269, "address": "Satellite"},
        {"city": "Ahmedabad", "pincode": "380054", "lat": 23.0406, "long": 72.5293, "address": "Vastrapur"},
        {"city": "Ahmedabad", "pincode": "380008", "lat": 22.9765, "long": 72.6023, "address": "Maninagar"},
        {"city": "Ahmedabad", "pincode": "380060", "lat": 23.0798, "long": 72.5151, "address": "SG Highway"},
        {"city": "Surat", "pincode": "395007", "lat": 21.1702, "long": 72.8311, "address": "Adajan Gam"},
        {"city": "Surat", "pincode": "395009", "lat": 21.1947, "long": 72.8084, "address": "City Light"},
        {"city": "Surat", "pincode": "395005", "lat": 21.2312, "long": 72.8213, "address": "Rander"},
        {"city": "Surat", "pincode": "394210", "lat": 21.1622, "long": 72.8582, "address": "Udhna"},
        {"city": "Surat", "pincode": "395006", "lat": 21.2036, "long": 72.8542, "address": "Varachha Road"}
    ],
    "Maharashtra": [
        {"city": "Mumbai", "pincode": "400001", "lat": 18.9220, "long": 72.8336, "address": "Colaba"},
        {"city": "Mumbai", "pincode": "400053", "lat": 19.1197, "long": 72.8424, "address": "Andheri West"},
        {"city": "Mumbai", "pincode": "400050", "lat": 19.0601, "long": 72.8367, "address": "Bandra West"},
        {"city": "Mumbai", "pincode": "400014", "lat": 19.0202, "long": 72.8495, "address": "Dadar East"},
        {"city": "Mumbai", "pincode": "400097", "lat": 19.1877, "long": 72.8472, "address": "Malad East"},
        {"city": "Pune", "pincode": "411038", "lat": 18.5068, "long": 73.8078, "address": "Kothrud"},
        {"city": "Pune", "pincode": "411005", "lat": 18.5295, "long": 73.8442, "address": "Shivajinagar"},
        {"city": "Pune", "pincode": "411045", "lat": 18.5645, "long": 73.7769, "address": "Baner"},
        {"city": "Pune", "pincode": "411057", "lat": 18.5932, "long": 73.7340, "address": "Hinjawadi"},
        {"city": "Pune", "pincode": "411028", "lat": 18.5194, "long": 73.9252, "address": "Magarpatta City"}
    ],
    "Uttar Pradesh": [
        {"city": "Lucknow", "pincode": "226001", "lat": 26.8467, "long": 80.9462, "address": "Hazratganj"},
        {"city": "Lucknow", "pincode": "226010", "lat": 26.8903, "long": 80.9390, "address": "Aliganj"},
        {"city": "Lucknow", "pincode": "226016", "lat": 26.9105, "long": 80.9653, "address": "Gomti Nagar"},
        {"city": "Lucknow", "pincode": "226004", "lat": 26.8407, "long": 80.9221, "address": "Charbagh"},
        {"city": "Lucknow", "pincode": "226021", "lat": 26.7850, "long": 80.9260, "address": "Indira Nagar"},
        {"city": "Kanpur", "pincode": "208001", "lat": 26.4607, "long": 80.3218, "address": "Civil Lines"},
        {"city": "Kanpur", "pincode": "208012", "lat": 26.4806, "long": 80.3340, "address": "Swaroop Nagar"},
        {"city": "Kanpur", "pincode": "208013", "lat": 26.4729, "long": 80.3466, "address": "Govind Nagar"},
        {"city": "Kanpur", "pincode": "208011", "lat": 26.4583, "long": 80.3650, "address": "Shyam Nagar"},
        {"city": "Kanpur", "pincode": "208002", "lat": 26.4523, "long": 80.3330, "address": "Mall Road"}
    ],
    "Karnataka": [
        {"city": "Bengaluru", "pincode": "560001", "lat": 12.9716, "long": 77.5946, "address": "MG Road"},
        {"city": "Bengaluru", "pincode": "560076", "lat": 12.9000, "long": 77.5850, "address": "JP Nagar"},
        {"city": "Bengaluru", "pincode": "560102", "lat": 12.8508, "long": 77.6616, "address": "Electronic City"},
        {"city": "Bengaluru", "pincode": "560095", "lat": 12.9606, "long": 77.6412, "address": "Indiranagar"},
        {"city": "Bengaluru", "pincode": "560103", "lat": 13.0283, "long": 77.5917, "address": "Yelahanka"},
        {"city": "Mysuru", "pincode": "570001", "lat": 12.2958, "long": 76.6394, "address": "Devaraja Mohalla"},
        {"city": "Mysuru", "pincode": "570017", "lat": 12.2718, "long": 76.6746, "address": "Vijayanagar"},
        {"city": "Mysuru", "pincode": "570008", "lat": 12.3052, "long": 76.6528, "address": "Lashkar Mohalla"},
        {"city": "Hubli", "pincode": "580020", "lat": 15.3647, "long": 75.1240, "address": "Dharwad Road"},
        {"city": "Hubli", "pincode": "580023", "lat": 15.3667, "long": 75.0867, "address": "Navanagar"}
    ],
    "Tamil Nadu": [
        {"city": "Chennai", "pincode": "600001", "lat": 13.0827, "long": 80.2707, "address": "Parrys Corner"},
        {"city": "Chennai", "pincode": "600020", "lat": 13.0100, "long": 80.2442, "address": "Adyar"},
        {"city": "Chennai", "pincode": "600036", "lat": 13.0352, "long": 80.2357, "address": "Anna Nagar"},
        {"city": "Chennai", "pincode": "600089", "lat": 13.0483, "long": 80.1860, "address": "Porur"},
        {"city": "Chennai", "pincode": "600100", "lat": 12.9166, "long": 80.2294, "address": "Velachery"},
        {"city": "Coimbatore", "pincode": "641001", "lat": 11.0168, "long": 76.9558, "address": "Town Hall"},
        {"city": "Coimbatore", "pincode": "641015", "lat": 11.0450, "long": 76.9844, "address": "RS Puram"},
        {"city": "Coimbatore", "pincode": "641035", "lat": 11.0254, "long": 77.0054, "address": "Peelamedu"},
        {"city": "Madurai", "pincode": "625001", "lat": 9.9252, "long": 78.1198, "address": "Meenakshi Amman Temple"},
        {"city": "Madurai", "pincode": "625020", "lat": 9.9402, "long": 78.1128, "address": "KK Nagar"}
    ]
}


# Utility Functions
def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def create_image(name):
    """
    Generate a placeholder image with text on it.
    
    :param name: The name of the image file (used for text and file naming).
    :return: ContentFile object with the image.
    """
    # Create a blank image (red background in this case)
    img = Image.new('RGB', (100, 100), color=(255, 0, 0))
    
    # Initialize ImageDraw to add text
    draw = ImageDraw.Draw(img)

    # Load font (fallback to default if ttf file is not available)
    try:
        font = ImageFont.truetype("arial.ttf", 12)  # Adjust font size as needed
    except IOError:
        font = ImageFont.load_default()
    
    # Text to display on the image
    text = f"{name}"
    
    # Get text size and calculate position to center it
    text_width, text_height = 25, 30
    text_x = (img.width - text_width) // 2
    text_y = (img.height - text_height) // 2
    
    # Add text to the image
    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)  # White text
    
    # Save the image to a buffer
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    
    # Return ContentFile for Django storage
    return ContentFile(buffer.getvalue(), name=f"{name}.jpg")

# Data Generation
def create_users_and_profiles():
    """Create customers and vendors."""
    # Create Customers
    for i in range(1, 201):  # 200 customers
        email = f"customer{i}@example.com"
        user = User.objects.create_user(
            email=email,
            username=f"customer{i}",
            firstname=f"First{i}",
            lastname=f"Last{i}",
            password=f'customer{i}'
        )
        user.role = 1
        user.is_active = True
        user.phone_no = f'80102991{i}'
        user.save()
        location = random.choice(random.choice(list(LOCATIONS.values())))
        profile = userProfile.objects.create(
            user=user,
            profile_pic=create_image(f"customer{i}_profile"),
            address=location["address"],
            city=location["city"],
            state=list(LOCATIONS.keys())[0],  # Just use the first state for simplicity
            country="India",
            pincode=location["pincode"],
            latitude=str(location["lat"]),
            longitude=str(location["long"]),
            location=Point(location["long"], location["lat"]),
        )
    locations = list(LOCATIONS.values())
    locations_state = list(LOCATIONS.keys())
    # Create Vendors
    for i in range(1, 51):  # 50 vendors
        email = f"vendor{i}@example.com"
        user = User.objects.create_user(
            email=email,
            username=f"vendor{i}",
            firstname=f"VendorFirst{i}",
            lastname=f"VendorLast{i}",
            password=f'vendor{i}'
        )
        user.is_active = True
        user.role = 2
        user.phone_no = f'90102991{i}'
        user.save()
        location = locations[(i-1)//10][(i-1)%10]
        profile = userProfile.objects.create(
            user=user,
            profile_pic=create_image(f"vendor{i}_profile"),
            address=location["address"],
            city=location["city"],
            state=locations_state[(i-1)//10],  # Just use the first state for simplicity
            country="India",
            pincode=location["pincode"],
            latitude=str(location["lat"]),
            longitude=str(location["long"]),
            location=Point(location["long"], location["lat"]),
        )
        profile.save()
        vendor = Vendor.objects.create(
            user=user,
            vendor_profile=profile,
            vendor_name=f"Vendor {i}",
            cover_pic=create_image(f"vendor{i}_cover"),
            slug=slugify(f"vendor-{i}"),
            vendor_license=create_image(f"vendor{i}_license"),
            is_approved=True,
        )
        vendor.save()

def create_food_categories_and_items():
    """Create food categories and items for vendors."""
    for vendor in Vendor.objects.all():
        for i in range(1, 6):  # 5 categories per vendor
            category_name = f"Category {i} for {vendor.vendor_name}"
            category = foodCategory.objects.create(
                vendor=vendor,
                category_name=category_name,
                slug=slugify(category_name),
                description=f"Description of {category_name}",
            )
            category.save()
            for j in range(1, 11):  # 10 items per category
                food_name = f"Food {j} in {category.category_name}"
                food=foodItem.objects.create(
                    vendor=vendor,
                    category=category,
                    food_name=food_name,
                    slug=slugify(food_name),
                    description=f"Delicious {food_name}",
                    image=create_image(food_name),
                    price=Decimal(random.randint(100, 1000)) / 10,
                    is_available=random.choice([True, False]),
                )
                food.save()

def create_carts_and_taxes():
    """Create carts and tax entries."""
    for user in User.objects.filter(role=User.customer):
        for i in range(1, 6):  # 5 cart items per user
            food_item = random.choice(foodItem.objects.all())
            Cart.objects.create(
                user=user,
                fooditem=food_item,
                quantity=random.randint(1, 5),
            )

    # Create tax entries
    Tax.objects.bulk_create([
        Tax(type="GST", percentage=5.0),
        Tax(type="Service Tax", percentage=10.0),
    ])

def create_opening_hours():
    """Create opening hours for vendors."""
    for vendor in Vendor.objects.all():
        for day_value, day_name in DAYS:
            OpeningHours.objects.create(
                vendor=vendor,
                day=day_value,
                from_hour="09:30 AM",
                to_hour="11:30 PM",
                is_closed=False,
            )

# Main Execution
if __name__ == "__main__":
    create_users_and_profiles()
    create_food_categories_and_items()
    create_carts_and_taxes()
    create_opening_hours()
    print("Data generation complete!")
