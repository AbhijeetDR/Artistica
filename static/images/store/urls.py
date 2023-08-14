from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart, name = 'cart'),
    path('', views.store, name = 'store'),
    path('checkout/', views.checkout, name = 'checkout'),
    path('update_item/', views.updateItem, name='update_item'),
    path('product/<int:pk>/', views.product, name='product'),

    path('process_order/', views.processOrder, name='process_order'),
    path('login/', views.login_user, name = 'login'),
    path('register/', views.register_user, name = 'register'),
    path('logout/', views.logout_user, name='logout'),

    path('profile/', views.profile, name='profile'),
    path('order_summary/<int:order_id>', views.order_summary, name='order_summary')

]