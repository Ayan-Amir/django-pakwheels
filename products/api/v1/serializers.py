from django.contrib.auth.models import User
from rest_framework import serializers

from products.models import Category, Favorite, GlobalStatsSnapshot, Product, ProductImage, ProductInfo, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'created', 'modified')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('id', 'image', 'created', 'modified')
        read_only_fields = ('id', 'created', 'modified')


class ProductInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInfo
        fields = ('id', 'makes', 'mileage', 'model', 'created', 'modified')
        read_only_fields = ('id', 'created', 'modified')


class ReviewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class ProductReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'rating', 'review', 'user', 'created', 'modified')
        read_only_fields = ('id', 'user', 'created', 'modified')

    def validate(self, attrs):
        request = self.context.get('request')
        product = self.context.get('product')
        user = request.user
        
        if Review.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError('You have already reviewed this product.')
        return attrs


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'price',
            'location',
            'status',
            'lat',
            'lng',
            'category',
            'created',
            'modified',
        )
        
class ProductFilterSerializer(serializers.Serializer):
    query = serializers.CharField(required=False, allow_blank=True)
    category = serializers.IntegerField(required=False)
    min_price = serializers.DecimalField(required=False, max_digits=12, decimal_places=2)
    max_price = serializers.DecimalField(required=False, max_digits=12, decimal_places=2)
    location = serializers.CharField(required=False, allow_blank=True)
    

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    product_info = ProductInfoSerializer(source='productinfo', read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    has_reviewed = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'price',
            'location',
            'status',
            'lat',
            'lng',
            'description',
            'category',
            'images',
            'product_info',
            'reviews',
            'is_favorited',
            'has_reviewed',
            'created',
            'modified',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        
        return Favorite.objects.filter(user=request.user, product=obj).exists()

    def get_has_reviewed(self, obj):
        request = self.context.get('request')
        
        return Review.objects.filter(user=request.user, product=obj).exists()


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'title',
            'price',
            'location',
            'lat',
            'lng',
            'status',
            'description',
            'category',
        )


class GlobalStatsSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalStatsSnapshot
        fields = ('id', 'total_products', 'total_reviews', 'total_favorites', 'created', 'modified')
        read_only_fields = ('id', 'created', 'modified')
