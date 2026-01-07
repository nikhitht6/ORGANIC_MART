from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from accounts.models import Profile


# =========================
# CUSTOMER CART FUNCTIONS
# =========================

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    raw_quantity = request.POST.get('quantity', '1')

    try:
        quantity = int(float(raw_quantity))
    except ValueError:
        messages.error(request, "Please enter a valid quantity.")
        return redirect('product_detail', product_id=product.id)
    if quantity < 1:
        messages.error(request, "Quantity must be at least 1.")
        return redirect('product_detail', product_id=product.id)


    # Prevent farmer buying own product 
    if product.farmer == request.user:
        messages.error(
            request,
            "You cannot purchase your own product."
        )
        return redirect('product_list')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if created:
        item.quantity = quantity
    else:
        item.quantity += quantity

    item.save()
    return redirect('view_cart')



@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()
    total = sum(item.subtotal() for item in items)

    return render(request, 'orders/cart.html', {
        'items': items,
        'total': total
    })


@login_required
def update_quantity(request, item_id, action):
    item = get_object_or_404(CartItem, id=item_id)

    if action == 'increase':
        item.quantity += 1
    elif action == 'decrease' and item.quantity > 1:
        item.quantity -= 1
    else:
        item.delete()
        return redirect('view_cart')

    item.save()
    return redirect('view_cart')



@login_required
def order_success(request):
    return render(request, 'orders/order_success.html')



# =========================
# CHECKOUT 
# =========================

import re

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    items = cart.items.all()

    #  CART EMPTY CHECK
    if not items.exists():
        messages.error(
            request,
            "Your cart is empty.",
            extra_tags='checkout'
        )
        return redirect('view_cart')

    total = sum(item.subtotal() for item in items)

    
    profile = Profile.objects.get(user=request.user)

    # SHOW CHECKOUT PAGE
    if request.method == 'GET':
        return render(request, 'orders/checkout.html', {
            'items': items,
            'total': total,
            'profile': profile,
        })

    # HANDLE FORM SUBMISSION
    shipping_address = request.POST.get('shipping_address', '').strip()
    payment_method = request.POST.get('payment_method')

    # =========================
    # SHIPPING ADDRESS VALIDATION
    # =========================
    if not shipping_address:
        messages.error(
            request,
            "Shipping address is required.",
            extra_tags='checkout'
        )
        return redirect('checkout')

    if len(shipping_address) < 15:
        messages.error(
            request,
            "Shipping address must be at least 15 characters long.",
            extra_tags='checkout'
        )
        return redirect('checkout')

    if not re.search(r'[A-Za-z]', shipping_address):
        messages.error(
            request,
            "Shipping address must include street or city name.",
            extra_tags='checkout'
        )
        return redirect('checkout')

    if not re.search(r'\d', shipping_address):
        messages.error(
            request,
            "Shipping address must include house number or pincode.",
            extra_tags='checkout'
        )
        return redirect('checkout')

    if not re.search(r'\b\d{6}\b', shipping_address):
        messages.error(
            request,
            "Shipping address must include a valid 6-digit pincode.",
            extra_tags='checkout'
        )
        return redirect('checkout')

    # =========================
    # PAYMENT METHOD VALIDATION
    # =========================
    if not payment_method:
        messages.error(
            request,
            "Please select a payment method.",
            extra_tags='checkout'
        )
        return redirect('checkout')

    # ONLINE PAYMENT 
    if payment_method == 'ONLINE':
        messages.info(
            request,
            "Online payment gateway integration is in progress. "
            "Please choose Cash on Delivery for now.",
            extra_tags='checkout'
        )
        return redirect('checkout')

    # =========================
    # STOCK VALIDATION
    # =========================
    for item in items:
        if item.quantity > item.product.stock:
            messages.error(
                request,
                f"Insufficient stock for {item.product.name}. "
                f"Available: {item.product.stock}",
                extra_tags='checkout'
            )
            return redirect('view_cart')

    # =========================
    # CREATE ORDER
    # =========================
    order = Order.objects.create(
        user=request.user,
        total_amount=total,
        shipping_address=shipping_address,
        payment_method=payment_method
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity
        )

        item.product.stock -= item.quantity
        item.product.save()

    items.delete()

    return redirect('order_success')


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == 'Pending':
        order.status = 'Cancelled'
        order.save()

    return redirect('customer_dashboard')


# =========================
# CUSTOMER ORDER 
# =========================

@login_required
def customer_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'orders/customer_orders.html', {
        'orders': orders
    })

@login_required
def customer_order_detail(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    items = OrderItem.objects.filter(
        order=order
    ).select_related('product')

    return render(request, 'orders/customer_order_detail.html', {
        'order': order,
        'items': items
    })

@login_required
def remove_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('view_cart')




# =========================
# FARMER ORDER MANAGEMENT
# =========================

@login_required
def farmer_orders(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role != 'FARMER':
        return redirect('customer_dashboard')

    orders = Order.objects.filter(
        items__product__farmer=request.user
    ).distinct().order_by('-created_at')


    return render(request, 'orders/farmer_orders.html', {
        'orders': orders
    })


@login_required
def update_order_status(request, order_item_id, status):
    profile = Profile.objects.get(user=request.user)

    # Only FARMER can access
    if profile.role != 'FARMER':
        return redirect('customer_dashboard')

    
    order_item = get_object_or_404(
        OrderItem,
        id=order_item_id,
        product__farmer=request.user
    )

    # Allowed transitions (PER ITEM)
    if order_item.status == 'Pending' and status == 'Shipped':
        order_item.status = 'Shipped'

    elif order_item.status == 'Shipped' and status == 'Delivered':
        order_item.status = 'Delivered'

    order_item.save()

    # =========================
    # UPDATE MAIN ORDER STATUS 
    # =========================
    order = order_item.order

    if order.items.filter(status__in=['Pending', 'Shipped']).exists():
        order.status = 'Shipped'
    else:
        order.status = 'Delivered'

    order.save()

    return redirect('farmer_orders')



@login_required
def farmer_order_detail(request, order_id):
    profile = Profile.objects.get(user=request.user)

    if profile.role != 'FARMER':
        return redirect('customer_dashboard')

    order = get_object_or_404(Order, id=order_id)

    items = OrderItem.objects.filter(
        order=order,
        product__farmer=request.user
    ).select_related('product')

    if not items.exists():
        return redirect('farmer_orders')

    return render(request, 'orders/farmer_order_detail.html', {
        'order': order,
        'items': items
    })



# =========================
# ADMIN — ORDERS
# =========================
@login_required
def admin_orders_view(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'accounts/admin_orders.html', {'orders': orders})


@login_required
def admin_update_order_status(request, order_id):
    profile = Profile.objects.get(user=request.user)

    if profile.role != 'ADMIN':
        return redirect('login')

    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        # Admin allowed actions
        if new_status == 'Cancelled':
            order.status = 'Cancelled'
            order.save()

        elif new_status in ['Shipped', 'Delivered']:
            
            order.status = new_status
            order.save()

    return redirect('admin_orders_view')

@login_required
def admin_order_detail(request, order_id):
    profile = Profile.objects.get(user=request.user)

    if profile.role != 'ADMIN':
        return redirect('customer_dashboard')

    order = get_object_or_404(Order, id=order_id)
    items = OrderItem.objects.filter(
        order=order
    ).select_related('product', 'product__farmer')

    return render(request, 'accounts/admin_order_detail.html', {
        'order': order,
        'items': items
    })
