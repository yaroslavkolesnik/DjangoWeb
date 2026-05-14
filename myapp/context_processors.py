from .cart import Cart
from .wishlist import Wishlist

def cart(request):
    return {'cart': Cart(request)}

def wishlist(request):
    return {'wishlist': Wishlist(request)}