from django.db import models


class ProductStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    SOLD = "sold", "Sold"
    PENDING = "pending", "Pending"
