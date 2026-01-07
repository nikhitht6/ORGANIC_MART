from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from orders.models import OrderItem

from .models import Profile
from products.models import Product
from orders.models import Order
from reviews.models import Review


# -------------------------
# LOGIN
# -------------------------
def login_view(request):
    if request.method == 'POST':
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )

        if user:
            login(request, user)
            profile, _ = Profile.objects.get_or_create(user=user)

            
            if user.is_superuser:
                profile.role = 'ADMIN'
                profile.is_verified = True
                profile.save()

            if profile.role == 'ADMIN':
                return redirect('admin_dashboard')

            if profile.role == 'FARMER':
                if not profile.is_verified:
                    return redirect('farmer_pending')
                return redirect('farmer_dashboard')

            return redirect('customer_dashboard')

        messages.error(request, "Invalid credentials")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    if request.method == 'POST':
        if request.POST['password1'] != request.POST['password2']:
            messages.error(request, "Passwords do not match")
            return redirect('register')

        user = User.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password1']
        )

        role = request.POST.get('role', 'CUSTOMER')

        Profile.objects.create(
            user=user,
            role=role,
            is_verified=False if role == 'FARMER' else True
        )

        login(request, user)
        return redirect('farmer_dashboard' if role == 'FARMER' else 'customer_dashboard')

    return render(request, 'accounts/register.html')


# =========================
# CUSTOMER
# =========================
@login_required
def customer_dashboard(request):
    profile = Profile.objects.get(user=request.user)

    
    if profile.is_blocked:
        messages.error(
            request,
            "Your account has been restricted. Please contact OrganicMart support."
        )
        return redirect('logout')

    categories = Product.objects.values_list(
        'category', flat=True
    ).distinct()

    featured_products = Product.objects.order_by('-created_at')[:6]

    ordered_categories = Product.objects.filter(
        orderitem__order__user=request.user
    ).values_list('category', flat=True)

    recommended_products = Product.objects.filter(
        category__in=ordered_categories
    ).exclude(
        orderitem__order__user=request.user
    ).distinct()[:4]

    return render(
        request,
        'accounts/customer_dashboard.html',
        {
            'categories': categories,
            'featured_products': featured_products,
            'recommended_products': recommended_products,
        }
    )


# =========================
# VIEW PROFILE
# =========================
@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'accounts/profile_view.html', {
        'profile': profile
    })


import re

# =========================
# EDIT PROFILE
# =========================
@login_required
def profile_edit(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        # =========================
        #  PHONE VALIDATION
        # =========================
        if phone:
            if not phone.isdigit() or len(phone) != 10:
                messages.error(
                    request,
                    "Phone number must contain exactly 10 digits."
                )
                return redirect('profile_edit')

        # =========================
        #  ADDRESS VALIDATION
        # =========================
        if address:
            # Minimum length
            if len(address) < 15:
                messages.error(
                    request,
                    "Address must be at least 15 characters long."
                )
                return redirect('profile_edit')

            # Must contain letters
            if not re.search(r'[A-Za-z]', address):
                messages.error(
                    request,
                    "Address must contain letters (street / city name)."
                )
                return redirect('profile_edit')

            # Must contain numbers
            if not re.search(r'\d', address):
                messages.error(
                    request,
                    "Address must contain numbers (house number or pincode)."
                )
                return redirect('profile_edit')

            # Must contain valid Indian pincode (6 digits)
            if not re.search(r'\b\d{6}\b', address):
                messages.error(
                    request,
                    "Address must include a valid 6-digit pincode."
                )
                return redirect('profile_edit')

        # =========================
        #  SAVE
        # =========================
        profile.phone = phone
        profile.address = address
        profile.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('profile_view')

    return render(request, 'accounts/profile_edit.html', {
        'profile': profile
    })




# =========================
# FARMER
# =========================
@login_required
def farmer_dashboard(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role != 'FARMER':
        return redirect('customer_dashboard')

    if profile.is_blocked:
        messages.error(
            request,
            "Your farmer account has been blocked by admin. "
            "Please contact OrganicMart for more information."
        )
        return redirect('logout')

    if not profile.is_verified:
        messages.info(request, "Your farmer account is pending verification.")
        return redirect('customer_dashboard')

    products = Product.objects.filter(
        farmer=request.user
    ).order_by('-created_at')

    orders = OrderItem.objects.filter(
        product__farmer=request.user
    ).select_related('order', 'product').order_by('-order__created_at')

    return render(request, 'accounts/farmer_dashboard.html', {
        'products': products,
        'orders': orders
    })


@login_required
def farmer_pending(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role != 'FARMER':
        return redirect('customer_dashboard')

    if profile.is_verified:
        return redirect('farmer_dashboard')

    return render(request, 'accounts/farmer_pending.html')


# =========================
# ADMIN DASHBOARD
# =========================
@login_required
def admin_dashboard(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'ADMIN':
        return redirect('customer_dashboard')

    context = {
        'users_count': Profile.objects.count(),
        'farmers_count': Profile.objects.filter(role='FARMER').count(),
        'orders_count': Order.objects.count(),
        'revenue': Order.objects.filter(status='Delivered')
                    .aggregate(total=Sum('total_amount'))['total'] or 0,
    }

    return render(request, 'accounts/admin_dashboard.html', context)


# =========================
# ADMIN — USERS
# =========================

@login_required
def admin_users(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'ADMIN':
        return redirect('customer_dashboard')

    profiles = Profile.objects.select_related('user')
    return render(request, 'accounts/admin_users.html', {'profiles': profiles})



@login_required
def toggle_user_block(request, profile_id):
    admin_profile = Profile.objects.get(user=request.user)

    if admin_profile.role != 'ADMIN':
        return redirect('customer_dashboard')

    profile = get_object_or_404(Profile, id=profile_id)

    #  ALLOW BLOCKING FARMER + CUSTOMER (ADMIN PROTECTED)
    if profile.role != 'ADMIN':
        profile.is_blocked = not profile.is_blocked
        profile.save()

    return redirect('admin_users')


@login_required
def verify_farmer(request, profile_id):
    admin_profile = Profile.objects.get(user=request.user)

    if admin_profile.role != 'ADMIN':
        return redirect('customer_dashboard')

    profile = get_object_or_404(Profile, id=profile_id, role='FARMER')
    profile.is_verified = True
    profile.save()

    return redirect('admin_users')


@login_required
def dashboard_redirect(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role == 'ADMIN':
        return redirect('admin_dashboard')

    if profile.role == 'FARMER':
        if not profile.is_verified:
            return redirect('farmer_pending')
        return redirect('farmer_dashboard')

    return redirect('customer_dashboard')
