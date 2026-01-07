from django.shortcuts import render
from products.models import Product
from reviews.models import Review


def home(request):
    
    featured_products = Product.objects.order_by('-created_at')[:6]
    categories = Product.objects.values_list('category', flat=True).distinct()

    return render(request, 'core/home.html', {
        'featured_products': featured_products,
        'categories': categories,
        
    })
