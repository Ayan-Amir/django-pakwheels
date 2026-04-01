from django.contrib import admin
from .models import Category, Product, ProductImage, ProductInfo, Favorite, Review, GlobalStatsSnapshot


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductInfoInline(admin.StackedInline):
    model = ProductInfo
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'price', 'location', 'status')
    list_filter = ('status', 'category')
    search_fields = ('title', 'description', 'location')
    list_editable = ('status',)
    raw_id_fields = ('category',)
    inlines = [ProductImageInline, ProductInfoInline]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')
    list_filter = ('product',)
    raw_id_fields = ('product',)


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ('product', 'makes', 'model', 'mileage')
    search_fields = ('makes', 'model')
    raw_id_fields = ('product',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    list_filter = ('user',)
    search_fields = ('user__username', 'product__title')
    raw_id_fields = ('user', 'product')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating')
    list_filter = ('rating',)
    search_fields = ('user__username', 'product__title', 'review')
    raw_id_fields = ('product', 'user')


@admin.register(GlobalStatsSnapshot)
class GlobalStatsSnapshotAdmin(admin.ModelAdmin):
    list_display = ('id', 'total_products', 'total_reviews', 'total_favorites', 'created')
    list_filter = ('created',)
    ordering = ('-created',)
