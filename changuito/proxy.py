from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.conf import settings

from . import models

try:
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone

try:
    cart_model = settings.CART_MODEL
    app_label, model_name = cart_model.split('.')
    Cart = apps.get_model(app_label, model_name)
except AttributeError:
    from .models import Cart

CART_ID = 'CART-ID'


class ItemAlreadyExists(Exception):
    pass


class ItemDoesNotExist(Exception):
    pass


class CartDoesNotExist(Exception):
    pass


class UserDoesNotExist(Exception):
    pass


class CartProxy(object):
    def __init__(self, request):
        user = request.user
        try:
            # First search by user
            if not user.is_anonymous():
                cart = Cart.objects.get(user=user, checked_out=False)
            # If not, search by request id
            else:
                user = None
                cart_id = request.session.get(CART_ID)
                cart = Cart.objects.get(id=cart_id, checked_out=False)
        except:
            cart = self.new(request, user=user)

        self.cart = cart

    def __iter__(self):
        for item in self.cart.items.all():
            yield item

    @classmethod
    def get_cart(self, request):
        cart_id = request.session.get(CART_ID)
        if cart_id:
            cart = Cart.objects.get(id=cart_id, checked_out=False)
        else:
            cart = None
        return cart

    def new(self, request, user=None):
        cart = Cart(creation_date=timezone.now(), user=user)
        cart.save()
        request.session[CART_ID] = cart.id
        return cart

    def add(self, product, unit_price, quantity=1):
        try:
            ctype = ContentType.objects.get_for_model(type(product),
                                                      for_concrete_model=False)
            item = self.cart.items.get(product=product,
                                       content_type=ctype)
        except models.Item.DoesNotExist:
            item = models.Item.objects.create(
                product=product,
                unit_price=unit_price,
                quantity=quantity
            )
            self.cart.items.add(item)
        else:
            item.quantity += quantity
            item.save()

        return item

    def remove_item(self, item_id):
        try:
            self.cart.items.get(id=item_id).delete()
        except models.Item.DoesNotExist:
            raise ItemDoesNotExist

    def update(self, product, quantity, *args):
        try:
            item = self.cart.items.get(object_id=product.id,
                                       content_type=product.content_type)
            item.quantity = quantity
            item.save()
        except models.Item.DoesNotExist:
            raise ItemDoesNotExist
        return self.cart

    def delete_old_cart(self, user):
        try:
            cart = Cart.objects.get(user=user)
            cart.delete()
        except Cart.DoesNotExist:
            pass

    def is_empty(self):
        return self.cart.is_empty()

    def replace(self, cart_id, new_user):
        try:
            self.delete_old_cart(new_user)
            cart = Cart.objects.get(pk=cart_id)
            cart.user = new_user
            cart.save()
            return cart
        except Cart.DoesNotExist:
            raise CartDoesNotExist

    def clear(self):
        for item in self.cart.items.all():
            item.delete()

    def get_item(self, item):
        try:
            obj = models.Item.objects.get(pk=item)
        except models.Item.DoesNotExist:
            raise ItemDoesNotExist

        return obj

    def get_last_cart(self, user):
        try:
            cart = Cart.objects.get(user=user, checked_out=False)
        except Cart.DoesNotExist:
            self.cart.user = user
            self.cart.save()
            cart = self.cart

        return cart

    def checkout(self):
        cart = self.cart
        try:
            cart.checked_out = True
            cart.save()
        except Cart.DoesNotExist:
            pass

        return cart
