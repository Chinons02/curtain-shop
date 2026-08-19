from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('design/<int:design_id>/', views.design_detail, name='design_detail'),
    path('customize/', views.customize_curtain, name='customize_curtain'),
    path('customize/<int:design_id>/', views.customize_curtain, name='customize_curtain_design'),
    path('cart/', views.cart, name='cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('calculate-price/', views.calculate_price_ajax, name='calculate_price'),
]
