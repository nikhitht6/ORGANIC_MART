from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product
from accounts.models import Profile


# -------------------------------
# PUBLIC PRODUCT LIST 
# -------------------------------
def product_list(request):
    products = Product.objects.all()

    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)

    return render(request, 'products/product_list.html', {
        'products': products
    })



# ---------------------------------
# FARMER: VIEW OWN PRODUCTS ONLY
# ---------------------------------
@login_required
def farmer_products(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role != 'FARMER':
        return redirect('product_list')

    # BLOCKED FARMER CHECK
    if profile.is_blocked:
        return render(request, 'accounts/farmer_blocked.html')

    products = Product.objects.filter(
        farmer=request.user
    ).order_by('-created_at')

    return render(request, 'products/farmer_products.html', {
        'products': products
    })


# -------------------------------
# FARMER: ADD PRODUCT
# -------------------------------
@login_required
def add_product(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role != 'FARMER':
        return redirect('product_list')

    
    if profile.is_blocked:
        return render(request, 'accounts/farmer_blocked.html')

    if request.method == 'POST':
        Product.objects.create(
            farmer=request.user,
            name=request.POST['name'],
            category=request.POST['category'],
            price=request.POST['price'],
            stock=request.POST['stock'],
            harvest_date=request.POST.get('harvest_date') or None,
            image=request.FILES['image']
        )
        return redirect('farmer_products')

    return render(request, 'products/add_product.html')


# -------------------------------
# FARMER: EDIT OWN PRODUCT ONLY
# -------------------------------
@login_required
def edit_product(request, pk):
    profile = Profile.objects.get(user=request.user)

    if profile.role != 'FARMER':
        return redirect('product_list')

    # BLOCKED FARMER CHECK
    if profile.is_blocked:
        return render(request, 'accounts/farmer_blocked.html')

    product = get_object_or_404(Product, pk=pk, farmer=request.user)

    if request.method == 'POST':
        product.name = request.POST['name']
        product.category = request.POST['category']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        product.harvest_date = request.POST.get('harvest_date') or None

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        return redirect('farmer_products')

    return render(request, 'products/edit_product.html', {
        'product': product
    })


# -------------------------------
# PRODUCT DETAIL + REVIEWS
# -------------------------------
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.filter(is_approved=True)

    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews
    })
