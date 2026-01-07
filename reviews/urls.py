from django.contrib import admin
from django.urls import path
from .views import add_review ,admin_review_action ,admin_reviews

urlpatterns = [
    path('add/<int:product_id>/', add_review, name='add_review'),

    path('admin/reviews/', admin_reviews, name='admin_reviews'),
    path('admin/reviews/<int:review_id>/<str:action>/', admin_review_action, name='admin_review_action'),
]
