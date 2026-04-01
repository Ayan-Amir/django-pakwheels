from celery import shared_task

from products.models import Favorite, Product, Review


@shared_task
def collect_global_stats_task():
    return {
        "total_products": Product.objects.count(),
        "total_reviews": Review.objects.count(),
        "total_favorites": Favorite.objects.count(),
    }
