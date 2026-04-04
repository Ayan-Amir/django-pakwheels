from celery import shared_task

from products.models import Favorite, GlobalStatsSnapshot, Product, Review


@shared_task
def collect_global_stats_task():
    snapshot = GlobalStatsSnapshot.objects.create(
        total_products=Product.objects.count(),
        total_reviews=Review.objects.count(),
        total_favorites=Favorite.objects.count(),
    )
    return {
        "id": snapshot.id,
        "total_products": snapshot.total_products,
        "total_reviews": snapshot.total_reviews,
        "total_favorites": snapshot.total_favorites,
        "created": snapshot.created.isoformat(),
    }
