from django.urls import path, include
from . import views
from accounts import views as AccountViews
urlpatterns = [
    path('', AccountViews.custDashboard, name='custDashboard'),
    path('customer_profile/', views.customer_profile, name='customer_profile'),
    path('my_orders/', views.my_orders, name="my_orders"),
    path('my_orders/<int:ord_id>', views.order_detail, name="order_detail"),
]
