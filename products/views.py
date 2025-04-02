from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Category, Type, Product
from .serializers import CategorySerializer, TypeSerializer, ProductSerializer
from backend_django_mv.authMiddle import JWTAuthentication



class CategoryList(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [JWTAuthentication]

class CategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [JWTAuthentication]


class TypeList(generics.ListCreateAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer
    permission_classes = [JWTAuthentication]

class TypeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer
    permission_classes = [JWTAuthentication]


class ProductList(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [JWTAuthentication]

    def get_queryset(self):
        queryset = Product.objects.all()
        category_id = self.request.query_params.get('category')
        type_id = self.request.query_params.get('type')

        if category_id:
            try:
                category = Category.objects.get(pk=category_id)
                queryset = queryset.filter(category=category)
            except Category.DoesNotExist:
                return Product.objects.none()  # Return an empty queryset if category does not exist

        if type_id:
            try:
                type_obj = Type.objects.get(pk=type_id)
                queryset = queryset.filter(type=type_obj)
            except Type.DoesNotExist:
                return Product.objects.none() # Return an empty queryset if type does not exist
        return queryset

    def list(self, request, *args, **kwargs): # Handles list request
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
