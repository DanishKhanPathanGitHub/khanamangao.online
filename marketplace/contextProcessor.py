from .models import Cart, Tax
from menu.models import foodItem

def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if  cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0
    return dict(cart_count=cart_count)

def get_cart_total(request):
    subtotal  = 0
    taxtotal = 0
    total = 0
    taxDict = {}
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            subtotal+=(item.fooditem.price*item.quantity)
    
        taxes = Tax.objects.filter(is_active=True)
        for tax in taxes:
            amount = round((tax.percentage * subtotal)/100, 2)
            taxtotal+=amount
            taxDict[tax.type] = [tax.percentage, amount]
        total = subtotal + taxtotal
    return dict(total=total, subtotal=subtotal, taxtotal=taxtotal, taxes=taxDict)