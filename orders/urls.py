from django.urls import path
from .views import (
    add_to_cart,
    view_cart,
    update_quantity,
    checkout,
    cancel_order,
    farmer_orders,
    update_order_status,order_success,
    customer_orders,
    admin_orders_view,
    admin_update_order_status,
    admin_order_detail,
    customer_order_detail,
    farmer_order_detail,
    remove_item
    
)

urlpatterns = [
    # =========================
    # CUSTOMER ROUTES
    # =========================
    path('cart/', view_cart, name='view_cart'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('update/<int:item_id>/<str:action>/', update_quantity, name='update_quantity'),
    path('checkout/', checkout, name='checkout'),
    path('cancel/<int:order_id>/', cancel_order, name='cancel_order'),
    path('success/', order_success, name='order_success'),
    path('my-orders/', customer_orders, name='customer_orders'),
    path('my-orders/<int:order_id>/',customer_order_detail,name='customer_order_detail'),
    path('remove/<int:item_id>/', remove_item, name='remove_item'),

    # =========================
    # FARMER ROUTES
    # =========================
    path('farmer/orders/', farmer_orders, name='farmer_orders'),
    path('farmer/update-item/<int:order_item_id>/<str:status>/',update_order_status, name='update_order_status'),

    path('farmer/orders/<int:order_id>/',farmer_order_detail,name='farmer_order_detail'),


    # =========================
    # ADMIN ROUTES
    # =========================
    path('admin/orders/', admin_orders_view, name='admin_orders_view'),
    path('admin/orders/update/<int:order_id>/', admin_update_order_status, name='admin_update_order_status'),
    path(
    'admin/orders/<int:order_id>/',admin_order_detail,name='admin_order_detail'),

]
