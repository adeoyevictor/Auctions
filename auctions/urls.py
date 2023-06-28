from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("create", views.create, name="create"),
    path("close", views.close, name="close"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("comment/<int:listing_id>", views.comment, name="comment"),
    path("listing/add_watchlist/<int:listing_id>", views.add_watchlist, name="add_watchlist"),
    path("listing/remove_watchlist/<int:listing_id>", views.remove_watchlist, name="remove_watchlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<str:category>", views.category, name="category")
]
