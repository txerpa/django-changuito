# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from decimal import Decimal
import pytest

from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpRequest

from changuito.models import Item
from changuito.proxy import CART_ID, CartProxy
from changuito.exceptions import CartDoesNotExist, ItemDoesNotExist


@pytest.fixture
def rqst():
    r = HttpRequest()
    r.session = {}
    return r


@pytest.fixture
def user():
    return User.objects.create(username='user_for_sell',
                               password='sold',
                               email='example@example.com')


@pytest.fixture
def anon_user():
    return AnonymousUser()


@pytest.fixture
def cart_proxy_anonuser(anon_user, rqst):
    rqst.user = anon_user
    rqst.cart = CartProxy(rqst)
    rqst.session[CART_ID] = rqst.cart.cart.id
    return rqst.cart


@pytest.mark.django_db
def _create_item_in_db(cart, content_object=None,
                       quantity=2, unit_price=125):
    item = Item.objects.create(content_object=content_object,
                               quantity=quantity,
                               unit_price=unit_price)
    cart.items.add(item)
    return item


@pytest.mark.django_db
def _create_item_in_request(cart_proxy, _user):
    item = cart_proxy.add_item(content_object=_user,
                               unit_price=Decimal('125'),
                               quantity=1)
    return item


@pytest.mark.django_db
def test_cart_clear(cart_proxy_anonuser, user, rqst):
    cart = cart_proxy_anonuser.get_cart(rqst)
    _create_item_in_db(cart, content_object=user)
    assert cart_proxy_anonuser.is_empty() is False
    cart_proxy_anonuser.clear_items()
    assert cart_proxy_anonuser.is_empty() is True


@pytest.mark.django_db
def test_cart_add_item(cart_proxy_anonuser, user):
    _create_item_in_request(cart_proxy_anonuser, user)
    assert cart_proxy_anonuser.is_empty() is False
    assert cart_proxy_anonuser.cart.total_price() == 125


@pytest.mark.django_db
def test_cart_remove_item(cart_proxy_anonuser, user, rqst):
    cart = cart_proxy_anonuser.get_cart(rqst)
    item = _create_item_in_db(cart, content_object=user)
    cart_proxy_anonuser.remove_item(item.id)
    assert cart_proxy_anonuser.is_empty() is True


@pytest.mark.django_db
def test_proxy_get_item(cart_proxy_anonuser, user, rqst):
    cart = cart_proxy_anonuser.get_cart(rqst)
    item = _create_item_in_db(cart, content_object=user)
    item_copy = cart_proxy_anonuser.get_item(item.id)
    assert item.id == item_copy.id
    assert item.quantity == item_copy.quantity


@pytest.mark.django_db
def test_proxy_cart_checkout(cart_proxy_anonuser, user, rqst):
    cart = cart_proxy_anonuser.get_cart(rqst)
    _create_item_in_db(cart, content_object=user)
    cart_proxy_anonuser.checkout()
    assert cart_proxy_anonuser.cart.checked_out is True


@pytest.mark.django_db
def test_new_cart_after_checkout_anon_user(cart_proxy_anonuser,
                                           rqst, anon_user):
    cart = cart_proxy_anonuser.cart
    cart_proxy_anonuser.checkout()
    assert cart.checked_out is True
    rqst.user = anon_user
    rqst.session = {}
    cart_proxy2 = CartProxy(rqst)
    assert cart != cart_proxy2.cart
    assert cart_proxy2.cart.checked_out is False


@pytest.mark.django_db
def test_new_cart_after_checkout_user(rqst, user):
    rqst.user = user
    cart_proxy = CartProxy(rqst)
    cart_proxy.checkout()
    assert cart_proxy.cart.checked_out is True
    cart_proxy2 = CartProxy(rqst)
    assert cart_proxy.cart != cart_proxy2.cart
    assert cart_proxy2.cart.checked_out is False


@pytest.mark.django_db
def test_cart_remove_unexistent_item(cart_proxy_anonuser):
    with pytest.raises(ItemDoesNotExist):
        cart_proxy_anonuser.remove_item(60)


@pytest.mark.django_db
def test_cart_update_item(cart_proxy_anonuser, user, rqst):
    cart = cart_proxy_anonuser.get_cart(rqst)
    item = _create_item_in_db(cart, content_object=user)
    assert cart_proxy_anonuser.is_empty() is False
    assert item.quantity == 2
    cart_proxy_anonuser.update_item_quantity(user, quantity=3)
    assert int(cart_proxy_anonuser.cart.items.all()[0].quantity) == 3


@pytest.mark.django_db
def test_user_n_carts(user, rqst):
    rqst.user = user
    cart_proxy = CartProxy(rqst)
    cart_proxy.checkout()
    cart_proxy = CartProxy(rqst)
    assert cart_proxy.n_carts(user) == 2


@pytest.mark.django_db
def test_get_user_last_cart(user, rqst):
    rqst.user = user
    cart_proxy = CartProxy(rqst)
    cart_proxy.checkout()
    cart_proxy = CartProxy(rqst)
    cart = cart_proxy.get_user_last_cart(user)
    assert cart_proxy.n_carts(user) == 2
    assert cart == cart_proxy.cart


@pytest.mark.django_db
def test_get_user_unexistent_last_cart_(user):
    with pytest.raises(CartDoesNotExist):
        CartProxy.get_user_last_cart(user)
