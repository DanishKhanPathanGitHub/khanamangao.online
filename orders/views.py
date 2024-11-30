from collections import defaultdict
from decimal import Decimal
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from accounts.utils import check_role_customer
from marketplace.contextProcessor import get_cart_counter,  get_cart_total
from datetime import datetime
import simplejson
from django.db import transaction

from marketplace.models import Cart, Tax
from .models import Order, OrderedFood, Payment
from .forms import OrderForm
from menu.models import foodItem
from accounts.models import User
from accounts.utils import send_notification

import razorpay
from food.settings import RZP_KEY_ID, RZP_KEY_SECRET
# Create your views here.

client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))

@user_passes_test(check_role_customer)
@login_required(login_url='login')
@require_POST
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    if get_cart_counter(request)["cart_count"] < 1:
        return redirect('marketplace')
    
    subtotal = get_cart_total(request)['subtotal']
    taxtotal = get_cart_total(request)['taxtotal']
    total = get_cart_total(request)['total']
    taxdata = get_cart_total(request)['taxes']


    order_form = OrderForm(request.POST)
    if order_form.is_valid():
        order = order_form.save(commit=False)
        order.user = request.user
        order.total = total
        order.total_tax = taxtotal
        order.tax_data = simplejson.dumps(taxdata)
        payment_method = request.POST.get('payment_method')
        order.save()
        order.order_number = datetime.now().strftime('%Y%m%d%H%M%S') + str(order.id)
        
        order.save()
        
        try:
            DATA = {
                "amount": int(float(order.total)*100),
                "currency": "INR",
                "receipt": "receipt #"+order.order_number,
                "notes": {
                    "key1": "value3",
                    "key2": "value2"
                }
            }
            rzp_order = client.order.create(data=DATA)
            rzp_order_id = rzp_order['id']
        except Exception as e:
            messages.error(request, "There was an error creating the payment. Please try again.")
            order.delete()
            return redirect('checkout')
        context = {
            'order':order,
            'payment_method':payment_method,
            'rzp_order_id':rzp_order_id,
            'cart_items':cart_items,
            'RZP_KEY_ID':RZP_KEY_ID,
            'rzp_amount':float(order.total)*100,
        }
        return render(request, 'orders/place_order.html', context)


@user_passes_test(check_role_customer)
@login_required(login_url='login')
@require_POST
def payments(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        try: 
            order_number = request.POST.get('order_number')
            transaction_id = request.POST.get('transaction_id')
            payment_method = request.POST.get('payment_method')
            status = request.POST.get('status')
            order = Order.objects.get(user=request.user, order_number=order_number)
            
            with transaction.atomic():
                
                payment = Payment.objects.create(
                    user = request.user,
                    transaction_id = transaction_id,
                    payment_method = payment_method,
                    amount  = order.total,
                    status = status
                )
                payment.save()
                
                order.payment = payment
                order.is_ordered = True 
                order.status = 'Completed' 
                order.payment.status = 'Paid'
                order.save()
                
                #moving cart items to ordered food and creating vendor specific order data
                vendor_totals = defaultdict(lambda: {'subtotal': 0, 'tax_total': 0, 'total': 0, 'tax_dict': {}})

                cart_items = Cart.objects.filter(user=request.user)
                taxes = Tax.objects.filter(is_active=True)
                for item in cart_items:
                    ordered_food = OrderedFood.objects.create(
                        order = order,
                        user = request.user,
                        fooditem = item.fooditem,
                        quantity = item.quantity,
                        price =  item.fooditem.price,
                        amount =  item.fooditem.price*item.quantity
                    )
                    ordered_food.save()
                    vendor_id = ordered_food.fooditem.vendor.id
                    vendor_totals[vendor_id]['subtotal'] += ordered_food.amount

                    taxtotal = Decimal(0)
                    taxDict = vendor_totals[vendor_id]['tax_dict']
                    
                    for tax in taxes:
                        amount = round((tax.percentage * ordered_food.amount) / 100, 2)
                        taxtotal += amount
                        if tax.type in taxDict:
                           taxDict[tax.type][1] += amount
                        else:
                            taxDict[tax.type] = [tax.percentage, amount]
                    
                    vendor_totals[vendor_id]['tax_total'] += taxtotal
                    vendor_totals[vendor_id]['total'] += (ordered_food.amount + taxtotal)
                    
                order.vendor_data = simplejson.dumps(vendor_totals) 
                order.created_at = datetime.now()
                order.save()
                
                #sending confirmation email to customer
                send_notification(
                    mail_subject="Your order confirmed!",
                    email_template="orders/order_confirmation_email.html",
                    context={
                        'order':order,
                        'user':request.user,
                        'domain':get_current_site(request)
                    },
                    to_emails= [order.email]
                )
            
                #sending confirmation email to vendor
                vendor_emails = {item.fooditem.vendor.user.email for item in cart_items}  
                send_notification(
                    mail_subject="You have received a new order!",
                    email_template="orders/order_received_email.html",
                    context={
                        'order': order,
                        'domain':get_current_site(request)
                    },
                    to_emails=list(vendor_emails)
                )
                cart_items.delete()
              
                return JsonResponse({'order_number':order_number})
        except Order.DoesNotExist:

            return JsonResponse({'error':'Order not found'}, status=404)
        except:
            order.status = 'Cancelled'
            order.payment.status = 'Cancelled'
            order.save()
            return JsonResponse({'error':'Order cancelled'}, status=404)