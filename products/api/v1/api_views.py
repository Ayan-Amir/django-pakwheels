from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Category, Favorite, Product, Review
from products.api.v1.serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductCreateSerializer,
    ProductReviewSerializer,
    ProductFilterSerializer
)
from products.tasks import create_product_task


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer


class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListCreateAPIView(generics.ListCreateAPIView):
    def get_queryset(self):
        qs = Product.objects.select_related('category', 'productinfo').prefetch_related('images',
        'reviews__user').all()
        
        filter_serializer = ProductFilterSerializer(data=self.request.query_params)
        
        if not filter_serializer.is_valid():
            return qs.none()
        
        filters = filter_serializer.validated_data
        
        text = filters.get('query')
        category_id = filters.get('category')
        min_price = filters.get('min_price')
        max_price = filters.get('max_price')
        location = filters.get('location')
        
        if text:
            qs = qs.filter(
                Q(title__icontains=text)
                | Q(description__icontains=text)
                | Q(location__icontains=text)
            )   
        if category_id:
            qs = qs.filter(category_id=category_id)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        if location:
            qs = qs.filter(location__icontains=location)

        return qs.order_by('created') 
        
       
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductListSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        product_payload = {
            'title': validated_data['title'],
            'price': str(validated_data['price']),
            'location': validated_data['location'],
            'lat': str(validated_data['lat']) if validated_data.get('lat') is not None else None,
            'lng': str(validated_data['lng']) if validated_data.get('lng') is not None else None,
            'status': validated_data['status'],
            'description': validated_data['description'],
            'category_id': validated_data['category'].id if validated_data.get('category') else None,
        }

        task = create_product_task.delay(product_payload)

        return Response(
            {
                'message': 'Product creation has been queued.',
                'task_id': task.id,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.select_related('category', 'productinfo').prefetch_related(
        'images',
        'reviews__user',
    ).all()
    serializer_class = ProductDetailSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        
        return context


class ProductFavoriteAPIView(generics.GenericAPIView):
    queryset = Product.objects.all()
    
    def post(self, request, pk):
        product = self.get_object()
        
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, 
            product=product
        )
        
        if not created:
            favorite.delete()
            return Response({'favorited': False})
            
        return Response({'favorited': True})


class ProductReviewAPIView(generics.CreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ProductReviewSerializer
    
    def get_serializer_context(self):
        """
        Pass the product and request into the serializer context.
        This is required for your 'already reviewed' validation logic.
        """
        context = super().get_serializer_context()
        context['product'] = get_object_or_404(Product, pk=self.kwargs.get('pk'))
        return context

    def perform_create(self, serializer):
        product = get_object_or_404(Product, pk=self.kwargs.get('pk'))
        serializer.save(user=self.request.user, product=product)
