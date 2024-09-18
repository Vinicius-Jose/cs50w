from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing", views.listing, name="listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("commentary/<int:listing_id>", views.commentary, name="commentary"),
    path("watchlist/<int:listing_id>", views.watchlist, name="watchlist"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category/<int:category_id>", views.category, name="category"),
    path("category", views.category, name="category"),
]
