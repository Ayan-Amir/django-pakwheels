from django.db import models

class ProductStatus(models.TextChoices):
    ACTIVE = "Active", "Active"
    SOLD = "Sold", "Sold"
    PENDING = "Pending", "Pending"
