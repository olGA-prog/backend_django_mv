from django.urls import path
from . import views

urlpatterns = [
    # URL для Category
    path('categories/', views.CategoryList.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.CategoryDetail.as_view(), name='category-detail'),

    # URL для Type
    path('types/', views.TypeList.as_view(), name='type-list'),
    path('types/<int:pk>/', views.TypeDetail.as_view(), name='type-detail'),

    # URL для Product
    path('products/', views.ProductList.as_view(), name='product-list'),
    path('products/<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
]