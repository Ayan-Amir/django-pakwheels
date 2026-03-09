from django.contrib import admin
from .models import *

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductInfo)
admin.site.register(Favorite)
admin.site.register(Review)
