from celery import shared_task

from products.models import Product


@shared_task
def create_product_task(product_payload):
    product = Product.objects.create(**product_payload)
    return product.id
