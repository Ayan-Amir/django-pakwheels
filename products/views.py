from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.decorators.http import require_GET
from django.db.models import Q

from .forms import ProductForm, ReviewForm
from .models import Product, Category, Favorite, Review

PRODUCTS_PER_PAGE = 1


@require_GET
def product_list(request):
    query = request.GET.get('query') or ''
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    location = request.GET.get('location')
    
    products = Product.objects.select_related('category').all()
    
    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query)
        )
        
    if category:
        products = products.filter(category_id=category)
        
    if min_price:
        products = products.filter(price__gte=min_price)
        
    if max_price:
        products = products.filter(price__lte=max_price)
        
    if location:
        products = products.filter(location__icontains=location)
        
    categories = Category.objects.all()

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, 'products/product_list.html', {
        'page_obj': page_obj,
        'query': query,
        'categories': categories,
    })

@login_required
@require_GET
def product_detail(request, id):
    product = get_object_or_404(Product.objects.select_related('category'), id=id)
    is_favorited = Favorite.objects.filter(user=request.user, product=product).exists()
    has_reviewed = Review.objects.filter(user=request.user, product=product).exists()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'is_favorited': is_favorited,
        'has_reviewed': has_reviewed,
    })


@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save()

            return redirect("product_list")

    else:
        form = ProductForm()

    return render(request, "products/add_product.html", {"form": form})


@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        favorite.delete()

    return redirect("product_detail", id=product.id)


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if Review.objects.filter(user=request.user, product=product).exists():
        return redirect("product_detail", id=product.id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect("product_detail", id=product.id)
    else:
        form = ReviewForm()

    return render(request, "products/add_review.html", {
        "form": form,
        "product": product
    })
