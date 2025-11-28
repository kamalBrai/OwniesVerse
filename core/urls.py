from django.urls import path
from .views import *

urlpatterns = [
    path("",index,name="index"),
    path("blog/",blog,name="blog"),
    path("blog/<slug:slug>/", blog_detail, name="blog_detail"),
    path("about_us/",about_us, name="about_us"),
    path("contact/", contact, name="contact"),
    path("search/",search,name="search"),
    path("product_detail/<int:id>",product_detail,name="product_detail"),
    path('cart/add/<int:id>/',cart_add, name='cart_add'),
    path('cart/item_clear/<int:id>/',item_clear, name='item_clear'),
    path('cart/item_increment/<int:id>/',item_increment, name='item_increment'),
    path('cart/item_decrement/<int:id>/',item_decrement, name='item_decrement'),
    path('cart/cart_clear/',cart_clear, name='cart_clear'),
    path('cart/cart-detail/',cart_detail, name='cart_detail'),

        # Wishlist URLs
    path('wishlist/', wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/toggle/<int:product_id>/', toggle_wishlist, name='toggle_wishlist'),

]
