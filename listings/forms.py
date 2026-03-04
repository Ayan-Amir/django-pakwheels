from django import forms
from .models import Product, Review


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "title",
            "price",
            "location",
            "lat",
            "lng",
            "status",
            "description",
        ]


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "review"]
