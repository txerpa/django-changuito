# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from datetime import datetime as timezone

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from .exceptions import CartDoesNotExist, ItemDoesNotExist
from .models import Item

try:
    cart_model = settings.CART_MODEL
    app_label, model_name = cart_model.split('.')
    Cart = apps.get_model(app_label, model_name)
except AttributeError:
    from .models import Cart

CART_ID = 'CART-ID'


class CartProxy(object):

    def __init__(self, request):
        self.cart = self.__class__.get_cart(request)

    def __iter__(self):
        for item in self.cart.items.all():
            yield item

    @classmethod
    def get_cart(cls, request):
        try:
            if request.user.is_anonymous:
                if CART_ID in request.session and request.session[CART_ID]:
                    cart_id = request.session.get(CART_ID)
                    cart = Cart.objects.get(id=cart_id, checked_out=False)
                else:
                    cart = cls.new_cart()
            else:
                cart = cls.get_user_last_cart(request.user)
        except CartDoesNotExist:
            cart = cls.new_cart(user=request.user)
        return cart

    @classmethod
    def new_cart(cls, user=None):
        return Cart.objects.create(creation_date=timezone.now(), user=user)

    def add_item(self, content_object, unit_price, quantity=1):
        try:
            item = self.cart.items.get(content_type=ContentType.objects
                                       .get_for_model(content_object),
                                       object_id=content_object.id)
            item.quantity += quantity
            item.save()
        except Item.DoesNotExist:
            item = Item.objects.create(
                quantity=quantity,
                unit_price=unit_price,
                content_object=content_object
            )
            self.cart.items.add(item)
        return item

    def remove_item(self, item_id):
        try:
            self.cart.items.get(id=item_id).delete()
        except Item.DoesNotExist:
            raise ItemDoesNotExist

    def get_item(self, item_id):
        try:
            item = self.cart.items.get(id=item_id)
        except Item.DoesNotExist:
            raise ItemDoesNotExist
        return item

    def clear_items(self):
        for item in self.cart.items.all():
            item.delete()

    def is_empty(self):
        return self.cart.is_empty()

    def update_item_quantity(self, content_object, quantity):
        try:
            item = self.cart.items.get(content_type=ContentType.objects
                                       .get_for_model(content_object),
                                       object_id=content_object.id)
            item.quantity = quantity
            item.save()
        except Item.DoesNotExist:
            raise ItemDoesNotExist

    @staticmethod
    def delete_user_last_cart(user):
        try:
            cart = Cart.objects.get(user=user)
            cart.delete()
        except Cart.DoesNotExist:
            pass

    @staticmethod
    def get_user_last_cart(user):
        return Cart.objects.filter(user=user, checked_out=False).order_by('creation_date').last()

    @staticmethod
    def n_carts(user):
        return Cart.objects.filter(user=user).count()

    def checkout(self):
        cart = self.cart
        cart.checked_out = True
        cart.save()
        return cart
