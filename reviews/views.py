from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from products.models import Product
from orders.models import OrderItem
from accounts.models import Profile


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    #  Prevent farmer reviewing own product
    if product.farmer == request.user:
        messages.error(
            request,
            "You cannot review your own product.",
            extra_tags='review'
        )
        return redirect('product_detail', product_id=product.id)

    # Allow review only if product was purchased AND delivered
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        product=product,
        order__status='Delivered'
    ).exists()

    if not has_purchased:
        messages.error(
            request,
            "You can review this product only after purchasing and receiving it.",
            extra_tags='review'
        )
        return redirect('product_detail', product_id=product.id)

    #  Prevent duplicate review
    if Review.objects.filter(user=request.user, product=product).exists():
        messages.error(
            request,
            "You have already reviewed this product.",
            extra_tags='review'
        )
        return redirect('product_detail', product_id=product.id)

    # =========================
    # HANDLE REVIEW SUBMISSION
    # =========================
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 0))

        # Rating validation
        if rating < 1 or rating > 5:
            messages.error(
                request,
                "Rating must be between 1 and 5.",
                extra_tags='review'
            )
            return redirect('add_review', product_id=product.id)

        Review.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            comment=request.POST.get('comment')
        )

        messages.success(
            request,
            "Review submitted successfully. It will be visible after admin approval.",
            extra_tags='review'
        )
        return redirect('product_detail', product_id=product.id)

    return render(request, 'reviews/add_review.html', {
        'product': product
    })


# =========================
# ADMIN — REVIEWS
# =========================


@login_required
def admin_reviews(request):
    profile = Profile.objects.get(user=request.user)
    if profile.role != 'ADMIN':
        return redirect('customer_dashboard')

    reviews = Review.objects.all().order_by('rating', '-created_at')
    return render(request, 'accounts/admin_reviews.html', {'reviews': reviews})



@login_required
def admin_review_action(request, review_id, action):
    review = get_object_or_404(Review, id=review_id)

    if action == 'approve':
        review.is_approved = True
    elif action == 'reject':
        review.is_approved = False

    review.save()
    return redirect('admin_reviews')


