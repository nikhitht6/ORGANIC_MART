from django.urls import path
from .views import *

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('dashboard/', dashboard_redirect, name='dashboard'),


    path('dashboard/customer/', customer_dashboard, name='customer_dashboard'),
    path('profile/', profile_view, name='profile_view'),
    path('profile/edit/', profile_edit, name='profile_edit'),


    path('dashboard/farmer/', farmer_dashboard, name='farmer_dashboard'),
    path('dashboard/farmer/pending/', farmer_pending, name='farmer_pending'),
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),

    path('admin/users/', admin_users, name='admin_users'),
    path('admin/users/block/<int:profile_id>/', toggle_user_block, name='toggle_user_block'),
    path('admin/users/verify/<int:profile_id>/', verify_farmer, name='verify_farmer'),

    

    
]
