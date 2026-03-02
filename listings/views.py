from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product


def product_list(request):
    query = request.GET.get('query')
    
    products = Product.objects.select_related('user', 'category').all()
    
    if query:
        products = products.filter(title__icontains=query)
        
    return render(request, 'listings/product_list.html', {'products': products, 'query': query})

def product_detail(request, id):
    product = get_object_or_404(Product.objects.select_related('user', 'category'), id=id)
    return render(request, 'listings/product_detail.html', {'product': product})


@login_required
def add_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)

        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()

            return redirect("home")   # redirect after submit

    else:
        form = ProductForm()

    return render(request, "listings/add_product.html", {"form": form})
