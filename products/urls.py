from django.urls import path
from .views import (
    product_list,
    farmer_products,
    add_product,
    edit_product,
    product_detail,
)

urlpatterns = [
    path('', product_list, name='product_list'),

    path('farmer/', farmer_products, name='farmer_products'),
    path('farmer/add/', add_product, name='add_product'),
    path('farmer/edit/<int:pk>/', edit_product, name='edit_product'),
    path('<int:product_id>/', product_detail, name='product_detail'),

]
