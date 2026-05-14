from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='home'),
    path("about/", views.about, name='about'),
    path("contact/", views.contact, name='contact'),

    path("product/<slug:slug>/", views.product_detail, name='product_detail'),

    path("favorites/", views.favorites, name='favorites'),
    path('favorites/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('favorites/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    path("order/", views.order, name='order'),
    path("profile/", views.profile, name='profile'),

    path('feedback/', views.feedback_view, name='feedback'),
    path('thanks/', views.feedback_view, name='thanks'),

    path('wishlist/', views.wishlist_view, name='wishlist_view'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),
]