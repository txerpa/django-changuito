from django.conf import settings
from django.contrib import admin

from .models import Item

try:
    own_cart_model = settings.CART_MODEL
except AttributeError:
    from changuito.models import Cart
    own_cart_model = None

if not own_cart_model:

    class CartAdmin(admin.ModelAdmin):
        pass

    admin.site.register(Cart, CartAdmin)


class ItemAdmin(admin.ModelAdmin):
    pass


admin.site.register(Item, ItemAdmin)
