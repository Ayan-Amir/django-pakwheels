from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Favorite, Product, Review
from .serializers import (
    CategorySerializer,
    ProductDetailSerializer,
    ProductListSerializer,
    ProductWriteSerializer,
    ReviewSerializer,
)


def _products_base_queryset():
    return Product.objects.select_related('category', 'productinfo').prefetch_related(
        'images',
        'reviews__user',
    ).all()


def _products_filtered_for_request(request):
    """Same filters as the old template product list (query string params)."""
    qs = _products_base_queryset()
    text = request.query_params.get('query') or ''
    category_id = request.query_params.get('category')
    min_price = request.query_params.get('min_price')
    max_price = request.query_params.get('max_price')
    location = request.query_params.get('location')

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
    return qs.order_by('-created')


class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer


class CategoryDetailAPIView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListCreateAPIView(generics.ListCreateAPIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        return _products_filtered_for_request(self.request)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductWriteSerializer
        return ProductListSerializer


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = _products_base_queryset()
    serializer_class = ProductDetailSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class ProductFavoriteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        product = get_object_or_404(Product.objects.all(), pk=pk)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
        if not created:
            favorite.delete()
            return Response({'favorited': False})
        return Response({'favorited': True})


class ProductReviewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        product = get_object_or_404(Product.objects.all(), pk=pk)
        serializer = ReviewSerializer(
            data=request.data,
            context={'request': request, 'product': product},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user, product=product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
