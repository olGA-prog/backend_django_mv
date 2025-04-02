from django.urls import path
from . import views

urlpatterns = [
    # URL для User
    path('users/', views.UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),


    # URL для Order
    path('orders/', views.OrderList.as_view(), name='order-list'),
    path('orders/<int:pk>/', views.OrderDetail.as_view(), name='order-detail'),


    path('create_payment/', views.create_payment, name='create_payment'),

    path('add_to_basket/', views.add_to_basket, name='add_to_basket'),
    path('basket_items/', views.get_basket_items, name='get_basket_items'),
    path('basket_items/<int:user_id>/<int:item_id>/', views.update_basket_item, name='update_basket_item'),
    path('basket_items_delete/<int:user_id>/<int:item_id>/', views.remove_from_basket, name='remove_from_basket'),
    path('create_order/', views.create_order, name='create_order'),
]