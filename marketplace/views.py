from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.contrib import messages
from vendor.models import Vendor, OpeningHours
from menu.models import foodCategory, foodItem
from django.db.models import Prefetch
from django.db.models import Q
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.utils import check_role_customer
from accounts.models import User, userProfile
from .models import Cart
from orders.forms import OrderForm

from .contextProcessor import get_cart_counter, get_cart_total

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
import datetime
# Create your views here.


def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendors_count = vendors.count()
    context = {
        "vendors":vendors,
        "vendors_count": vendors_count,
    }
    return render(request, 'marketplace/listings.html', context)


def vendor_detail(request, slug):
    vendor = get_object_or_404(Vendor, slug=slug)
    categories = foodCategory.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'fooditems',
            queryset = foodItem.objects.filter(is_available=True)
        )
    )
    today = datetime.date.today().isoweekday()
    print(today)
    opening_hours = OpeningHours.objects.filter(vendor=vendor)
    print(opening_hours)
    if opening_hours:
        today_hours = opening_hours.filter(day=today)[0]

        if today_hours.is_closed:
            is_open = False
        else:
            from_hour = today_hours.from_hour 
            to_hour = today_hours.to_hour     
            print(today_hours, 'hdehfuuhuh  ::', from_hour, to_hour)
            # Convert the string times to datetime objects
            from_time = datetime.datetime.strptime(from_hour, "%I:%M %p").time()
            to_time = datetime.datetime.strptime(to_hour, "%I:%M %p").time()

            # Get the current time
            curr_time = datetime.datetime.now().time()
            print(curr_time, from_time, to_time)
            if from_time <= curr_time <= to_time:
                is_open = True
            else:
                is_open = False
    else:
        today_hours = None
        is_open = False
        print("The restaurant is closed.")

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        "vendor": vendor,
        "categories":categories,
        "cart_items":cart_items,
        "opening_hours":opening_hours,
        "today_hour":today_hours,
        "is_open":is_open,
    }
    return render(request, 'marketplace/vendor_detail.html', context)

@user_passes_test(check_role_customer)
def add_to_cart(request, food_id=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                food_item = foodItem.objects.get(id=food_id)
                #check if user had already added food in cart
                try:
                    food_item_cart = Cart.objects.get(user=request.user, fooditem=food_item)
                    food_item_cart.quantity += 1
                    food_item_cart.save()
                    return JsonResponse(
                        {
                            'status':'success',
                            'message': 'quantity increased by one', 
                            'cart_counter':get_cart_counter(request), 
                            'qty':food_item_cart.quantity,
                            'get_cart_total':get_cart_total(request),
                        }
                    )
                except:
                    food_item_cart = Cart.objects.create(user=request.user, fooditem=food_item, quantity=1)
                    return JsonResponse(
                        {
                            'status':'success', 
                            'message':'food added to the cart', 
                            'cart_counter':get_cart_counter(request), 
                            'qty':food_item_cart.quantity,
                            'get_cart_total':get_cart_total(request),
                        }
                    )
                    
            except:
                return JsonResponse(
                    {
                        'status':'Failed', 
                        'message':'This food does not exist'
                    }
                )
        else:
            return JsonResponse(
                {
                    'status':'Failed', 
                    'message':'Invalid request'
                }
            )       
    else:
        return JsonResponse(
            {
                'status':'login_required',
                'message':'Please login to continue'
            }
        )

@user_passes_test(check_role_customer)
def decrease_cart(request, food_id=None):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                food_item = foodItem.objects.get(id=food_id)
                #check if user had already added food in cart
                try:
                    food_item_cart = Cart.objects.get(user=request.user, fooditem=food_item)
                    if food_item_cart.quantity > 1:
                        food_item_cart.quantity -= 1 
                        food_item_cart.save()
                    else:
                        food_item_cart.delete()
                        food_item_cart.quantity = 0
                    return JsonResponse({'status':'success', 'cart_counter':get_cart_counter(request), 'qty':food_item_cart.quantity, 'get_cart_total':get_cart_total(request)})
                except:
                    return JsonResponse({'status':'Failed', 'message':'You do not have this item in your cart'})
                    
            except:
                return JsonResponse({'status':'Failed', 'message':'This food does not exist'})
        else:
            return JsonResponse({'status':'Failed', 'message':'Invalid request'})
    else:
        return JsonResponse({'status':'login_required', 'message':'login to continue'})    
    
@login_required(login_url='login')
@user_passes_test(check_role_customer)
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        "cart_items":cart_items,
    }
    return render(request, 'marketplace/cart.html', context)

@user_passes_test(check_role_customer)
def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()   
                    return JsonResponse({'status':'success', 'message':'cart item deleted', 'cart_counter':get_cart_counter(request),'get_cart_total':get_cart_total(request)})   
            except:
                return JsonResponse({'status':'Failed', 'message':'cart item does not exist'})
        else:
            return JsonResponse({'status':'Failed', 'message':'invalid request'})

def search(request):
    if not "address" in request.GET:
        return redirect('marketplace')

    address = request.GET["address"]
    latitude = request.GET["lat"]
    longitude = request.GET["long"]
    radius = request.GET["radius"]
    name = request.GET["keyword"]
    print("hello search")
    print(latitude, longitude, radius)

    vendors = Vendor.objects.filter(
        Q(
            id__in=foodItem.objects.filter(
                food_name__icontains=name, is_available=True  
            ).values_list('vendor')
        ) |
        Q(
            vendor_name__icontains=name, is_approved=True, user__is_active=True,

        ) 
    )
    if longitude and latitude and radius:
        pnt = GEOSGeometry(f"POINT({longitude} {latitude})")
        print(pnt)
        vendors = vendors.filter(
            vendor_profile__location__distance_lte=(pnt, D(km=radius))
        ).annotate(
            distance=Distance('vendor_profile__location', pnt)
        ).order_by('distance')
    
    context = {
        "vendors": vendors,
        "vendors_count": vendors.count(),
    }

    return render(request, 'marketplace/listings.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    if get_cart_counter(request)["cart_count"] < 1:
        return redirect('marketplace')
    user = request.user
    user_profile = userProfile.objects.get(user=user)
    

    #checking if item in cart is available or not, and vendor providing item is closed or not
    for item in cart_items:
        if item.fooditem.is_available == False:
            messages.error(request, f'food item: {item.fooditem.food_name} is not available right now')
            return redirect('cart')
        today_hours = OpeningHours.objects.get(vendor=item.fooditem.vendor, day=datetime.date.today().isoweekday())
        is_open = False
        if today_hours.is_closed:
            pass
        else:
            from_hour = today_hours.from_hour 
            to_hour = today_hours.to_hour     

            from_time = datetime.datetime.strptime(from_hour, "%I:%M %p").time()
            to_time = datetime.datetime.strptime(to_hour, "%I:%M %p").time()

            curr_time = datetime.datetime.now().time()
            if from_time <= curr_time <= to_time:
                is_open = True
            else:
                pass
        if not is_open:
            messages.error(request, f'you have {item.fooditem.food_name} in your cart, which is served by {item.fooditem.vendor.vendor_name}! Which is closed right now!')
            return redirect('cart')


    initial_values = {
        'firstname':user.firstname,
        'lastname':user.lastname,
        'email':user.email,
        'address':user_profile.address,
        'country':user_profile.country,
        'state':user_profile.state,
        'city':user_profile.city,
        'pincode':user_profile.pincode,
    }
    order_form = OrderForm(initial=initial_values)
    context = {
        'order_form': order_form,
        'cart_items':cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)