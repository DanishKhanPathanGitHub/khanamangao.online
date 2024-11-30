from django.shortcuts import render, redirect, get_object_or_404
import simplejson
from accounts.models import userProfile, User
from accounts.forms import userProfileForm, UserUpdateForm
from django.contrib.auth.decorators import login_required, user_passes_test
from accounts.utils import check_role_customer
from django.contrib import messages
from orders.models import Order, OrderedFood
# Create your views here.
@login_required(login_url='login')    
@user_passes_test(check_role_customer)
def customer_profile(request):
    user_profile = get_object_or_404(userProfile, user=request.user)
    if request.POST:
        user_profile_form = userProfileForm(request.POST, request.FILES, instance=user_profile)
        user_detail_form = UserUpdateForm(request.POST, instance=request.user)
        if user_profile_form.is_valid() and user_detail_form.is_valid():
            user_profile_form.save()
            user_detail_form.save()
            messages.success(request, 'Changes saved succesfully!')
            return redirect('customer_profile')
    else:
        user_profile_form = userProfileForm(instance=user_profile)
        user_detail_form = UserUpdateForm(instance=request.user)

    context = {
        "user_profile_form":user_profile_form,
        "user_profile":user_profile,
        "user_detail_form":user_detail_form,
    }
    return render(request, 'customer/customer_profile.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('created_at')
    context = {
        'orders':orders,
    }
    return render(request, "customer/my_orders.html", context)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def order_detail(request, ord_id):
    try:
        order = Order.objects.get(order_number=ord_id)
        ordered_food = OrderedFood.objects.filter(order=order)
        tax_data = simplejson.loads(order.tax_data)
        subtotal = 0
        for item in ordered_food:
            subtotal+= item.fooditem.price * item.quantity 
        context = {
            'order':order,
            'ordered_food':ordered_food,
            'tax_data':tax_data,
            'subtotal':subtotal,
        }
        return render(request, 'customer/order_detail.html', context)
    except:
        messages.error(request, 'Invalid order details')
        return redirect('my_orders')