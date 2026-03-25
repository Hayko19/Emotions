from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<str:key>/', views.cart_update, name='cart_update'),
    path('cart/remove/<str:key>/', views.cart_remove, name='cart_remove'),
    path('checkout/', views.checkout, name='checkout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/order/<int:order_id>/update/', views.admin_order_update, name='admin_order_update'),
]

