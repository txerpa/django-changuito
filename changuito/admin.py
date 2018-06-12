# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.contrib import admin

from changuito.models import Cart

from .models import Item


class CartAdmin(admin.ModelAdmin):
    pass


admin.site.register(Cart, CartAdmin)


class ItemAdmin(admin.ModelAdmin):
    pass


admin.site.register(Item, ItemAdmin)
