from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django_extensions.db.models import TimeStampedModel
from .choices import STATUS_CHOICES


class Category(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    
    def __str__(self):
        return self.name

class Product(TimeStampedModel):
    location = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    title = models.CharField(max_length=255, db_index=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="products")
    description = models.TextField()
    
    def __str__(self):
        return self.title
    

class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='product_images/')
    
    def __str__(self):
        return f"{self.product.title} - {self.image.name}"

class ProductInfo(TimeStampedModel):
    makes = models.CharField(max_length=255)
    mileage = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.makes} {self.model}"
    
class Favorite(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="favorites")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product_favorite')
        ]
    
    def __str__(self):
        return f"{self.user.username} → {self.product.title}"

class Review(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    review = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product_review')
        ]

    def __str__(self):
        return f"{self.product.title} - {self.rating}"
