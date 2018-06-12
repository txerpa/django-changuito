# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from changuito.models import Cart
from django.conf import settings
from django.contrib import admin

from .models import Item

try:
    cart_model = settings.CART_MODEL
except AttributeError:
    from .models import Cart


if not cart_model:

    class CartAdmin(admin.ModelAdmin):
        pass


    admin.site.register(Cart, CartAdmin)


class ItemAdmin(admin.ModelAdmin):
    pass


admin.site.register(Item, ItemAdmin)
