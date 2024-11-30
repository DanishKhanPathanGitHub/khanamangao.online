import simplejson
from accounts.forms import userProfileForm
from accounts.models import userProfile
from orders.models import Order, OrderedFood
from .forms import vendorForm, openingHoursForm
from .models import *
from menu.models import foodCategory, foodItem
from menu.forms import foodCategoryForm, foodItemForm

from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpRequest, JsonResponse

from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.views import check_role_vendor


# Create your views here.
@login_required(login_url='login')    
@user_passes_test(check_role_vendor)
def profile(request):
    user_profile = get_object_or_404(userProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)
    if request.POST:
        user_profile_form = userProfileForm(request.POST, request.FILES, instance=user_profile)
        vendor_form = vendorForm(request.POST, request.FILES, instance=vendor)
        if user_profile_form.is_valid() and vendor_form.is_valid():
            user_profile_form.save()
            vendor_form.save()
            messages.success(request, 'Changes saved succesfully!')
            return redirect('profile')
    else:
        user_profile_form = userProfileForm(instance=user_profile)
        vendor_form = vendorForm(instance=vendor)

    context = {
        "user_profile_form":user_profile_form,
        "vendor_form":vendor_form,
        "user_profile":user_profile,
    }
    return render(request, 'vendor/vendorProfile.html', context)

@user_passes_test(check_role_vendor)
@login_required(login_url='login')
def my_orders(request):
    vendor = Vendor.objects.get(user=request.user)
    orders = Order.objects.filter(
        is_ordered=True,
        orderedfood__fooditem__vendor=vendor
    ).distinct().order_by('-created_at')
    
    vendor_orders = []
    
    for order in orders:
        vendor_data = simplejson.loads(order.vendor_data).get(str(vendor.id), None)
        if vendor_data:
            order_info = {
                'order_number': order.order_number,
                'date': order.created_at,
                'total': vendor_data['total'],
                'status': order.status
            }
            vendor_orders.append(order_info)
    
    context = {
        'vendor_orders': vendor_orders,
        'total_orders': len(vendor_orders),
    }
    return render(request, 'vendor/my_orders.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def order_detail(request, ord_id):
    vendor = Vendor.objects.get(user=request.user)
    try:
        order = Order.objects.get(order_number=ord_id)
        ordered_food = OrderedFood.objects.filter(order=order, fooditem__vendor=vendor)
        vendor_data = simplejson.loads(order.vendor_data).get(str(vendor.id), None)
        tax_data = vendor_data['tax_dict']
        subtotal = vendor_data['subtotal']
        total = vendor_data['total']

        context = {
            'order':order,
            'ordered_food':ordered_food,
            'tax_data':tax_data,
            'subtotal':subtotal,
            'total':total
        }
        return render(request, 'vendor/order_detail.html', context)
    except:
        messages.error(request, 'Invalid order details')
        return redirect('my_orders')

@login_required(login_url='login')    
@user_passes_test(check_role_vendor)
def menu_manager(request):
    vendor = Vendor.objects.get(user=request.user)
    categories = foodCategory.objects.filter(vendor=vendor)
    context ={
        "categories":categories,
    }
    return render(request, 'vendor/menu.html', context)

@login_required(login_url='login')    
@user_passes_test(check_role_vendor)
def foodItem_by_category(request, pk=None):
    vendor = Vendor.objects.get(user=request.user)
    category = get_object_or_404(foodCategory, pk=pk)
    food_items = foodItem.objects.filter(vendor=vendor, category=category).order_by('created_at')
    context = {
        "category":category,
        "food_items":food_items,
    }
    return render(request, 'vendor/foodItem_by_category.html', context)

@login_required(login_url='login')    
@user_passes_test(check_role_vendor)
def category_add(request):
    if request.POST:
        category_form = foodCategoryForm(request.POST)
        if category_form.is_valid():
            category = category_form.save(commit=False)
            category.vendor = Vendor.objects.get(user=request.user)
            category_form.save()
            messages.success(request, "category added succesfully")
            return  redirect('menu_manager')
        else:
            print("form is not valid")
            print(category_form.fields)
            print(category_form.errors)
    else: 
        category_form = foodCategoryForm()
        
    context = {
        "category_form":category_form,
    }
    return render(request, 'vendor/category_add.html', context)

@login_required(login_url='login')    
@user_passes_test(check_role_vendor)
def category_edit(request, pk=None):
    category = get_object_or_404(foodCategory, pk=pk)
    if request.POST:
        category_form = foodCategoryForm(request.POST, instance=category)
        if category_form.is_valid():
            category = category_form.save(commit=False)
            category.vendor = Vendor.objects.get(user=request.user)
            category_form.save()
            messages.success(request, "category updated succesfully")
            return  redirect('menu_manager')
        else:
            print("form is not valid")
            print(category_form.fields)
            print(category_form.errors)
    else: 
        category_form = foodCategoryForm(instance=category)
        
    context = {
        "category":category,
        "category_form":category_form,
    }
    return render(request, 'vendor/category_edit.html', context)

@login_required(login_url='login')    
@user_passes_test(check_role_vendor)
def category_delete(request, pk=None):
    category = get_object_or_404(foodCategory, pk=pk)
    category.delete()
    messages.success(request, "category has been deleted succesfully")
    return  redirect('menu_manager')



@login_required(login_url='login')    
@user_passes_test(check_role_vendor)
def food_add(request):
    vendor = Vendor.objects.get(user=request.user)
    food_item_form = foodItemForm(vendor_id=vendor.id)
    if request.POST:
        food_item_form = foodItemForm(request.POST, request.FILES, vendor_id=vendor.id)
        if food_item_form.is_valid():
            food_item = food_item_form.save(commit=False)
            food_item.vendor = Vendor.objects.get(user=request.user)
            food_item_form.save()
            messages.success(request, "food item added succesfully")
            return  redirect('foodItem_by_category', food_item.category.id)
        else:
            print("form is not valid")
            print(food_item_form.errors)
        
    context = {
        "food_item_form":food_item_form,
    }
    return render(request, 'vendor/food_add.html', context)       
    
@login_required(login_url='login')    
@user_passes_test(check_role_vendor)
def food_edit(request, pk=None):
    food = get_object_or_404(foodItem, pk=pk)
    vendor = Vendor.objects.get(user=request.user)
    if request.POST:
        food_item_form = foodItemForm(request.POST, request.FILES, instance=food, vendor_id=vendor.id)
        if food_item_form.is_valid():
            food_item = food_item_form.save(commit=False)
            food_item.vendor = Vendor.objects.get(user=request.user)
            food_item_form.save()
            messages.success(request, "food updated succesfully")
            return  redirect('foodItem_by_category', food_item.category.id)
        else:
            print("form is not valid")
            print(food_item_form.fields)
            print(food_item_form.errors)
            
    else: 
        food_item_form = foodItemForm(instance=food, vendor_id=vendor.id)
        
    context = {
        "food":food,
        "food_item_form":food_item_form,
    }
    return render(request, 'vendor/food_edit.html', context)

@login_required(login_url='login')    
@user_passes_test(check_role_vendor)
def food_delete(request, pk=None):
    food = get_object_or_404(foodItem, pk=pk)
    category = food.category
    food.delete()
    messages.success(request, "food has been deleted succesfully")
    return  redirect('foodItem_by_category', category.id)


@login_required(login_url='login')    
@user_passes_test(check_role_vendor)
def opening_hours(request):
    opening_hours = OpeningHours.objects.filter(vendor=Vendor.objects.get(user=request.user))
    form = openingHoursForm()
    context = {
        "opening_hours":opening_hours,
        "form":form,
    }
    return render(request, 'vendor/opening_hours.html', context)

@user_passes_test(check_role_vendor)
def opening_hours_add(request):
    if request.user.is_authenticated:
        vendor = Vendor.objects.get(user=request.user)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.POST:
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')=='true'

            hour = OpeningHours.objects.get(vendor=vendor, day=day)
            if hour:
                hour.from_hour = from_hour
                hour.to_hour = to_hour
                hour.is_closed = is_closed
                if hour.is_closed:
                    pass
                else:
                    time_format = "%I:%M %p"
                    from_time = datetime.strptime(from_hour, time_format)
                    to_time = datetime.strptime(to_hour, time_format)

                    if to_time <= from_time:
                        response = {
                            'status':'Failure',
                            'message':f'from_hour should be earlier than to_hour'
                        }
                        return JsonResponse(response)
                
                hour.save()
                if hour.is_closed:
                    response = {
                        'status':'success', 'id':hour.id, 
                        'is_closed':'Closed',
                        'message':f'{hour.get_day_display()} set to closed'
                    }
                else:
                    response = {
                        'status':'success', 'id':hour.id,
                        'from_hour':hour.from_hour, 'to_hour':hour.to_hour,
                        'message':f'Timing for {hour.get_day_display()} updated'
                    }
                return JsonResponse(response)
        else:
            return HttpResponse("Invalid request")
        
