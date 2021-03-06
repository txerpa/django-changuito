# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase

from changuito.models import Cart, Item

try:
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone


class CartItemsTestCase(TestCase):

    def setUp(self):
        self.cart = Cart.objects.create(creation_date=timezone.now(),
                                        checked_out=False)
        self.user = User.objects.create(username='user_for_sell',
                                        password='sold',
                                        email='example@example.com')

    def _create_item_in_db(self, content_object=None,
                           quantity=2, unit_price=125):
        item = Item.objects.create(content_object=content_object,
                                   quantity=quantity,
                                   unit_price=unit_price)
        self.cart.items.add(item)
        return item

    def test_cart_creation(self):
        self.assertEquals(self.cart.id, 1)
        self.assertEquals(self.cart.is_empty(), True, 'Cart must be empty')

    def test_item_creation(self):
        item = self._create_item_in_db(content_object=self.user)
        item_in_cart = self.cart.items.all()[0]
        self.assertEquals(item_in_cart, item, 'First item in cart should '
                                              'be equal the item we created')
        self.assertEquals(self.cart.is_empty(), False)
        self.assertEquals(item_in_cart.content_object, self.user,
                          'Product associated with the first item'
                          ' in cart should equal the user we\'re selling')
        self.assertEquals(item_in_cart.unit_price, Decimal('125'),
                          'Unit price of the first item stored'
                          ' in the cart should equal 125')
        self.assertEquals(item_in_cart.quantity, 2,
                          'The first item in cart should'
                          ' have 2 in it\'s quantity')

    def test_cart_total_price(self):
        self._create_item_in_db(content_object=self.user)
        self._create_item_in_db(content_object=self.user,
                                unit_price=Decimal('100.00'), quantity=1)
        self.assertEquals(self.cart.total_price(), 350, 'Price == (125*2)+100')

    def test_cart_total_quantity(self):
        obj_site = Site.objects.all()[:1]
        self._create_item_in_db(content_object=self.user,
                                unit_price=Decimal('400.00'), quantity=3)
        self._create_item_in_db(content_object=obj_site[0],
                                unit_price=Decimal('100.00'), quantity=1)
        self.assertEquals(self.cart.total_quantity(), 4)

    def test_cart_item_price(self):
        item = self._create_item_in_db(content_object=self.user,
                                       quantity=4, unit_price=Decimal('3.20'))
        self.assertEquals(float(item.total_price), float('12.80'))

    def test_item_unicode(self):
        item = self._create_item_in_db(content_object=self.user)
        self.assertEquals(item.__unicode__(),
                          '{} units of User {}'.format(2, self.user.id))

    def test_item_update_quantity(self):
        item = self._create_item_in_db(content_object=self.user)
        self.assertEquals(item.quantity, 2)
        item.update_quantity(7)
        self.assertEquals(item.quantity, 7)

    def test_item_update_contenttype(self):
        obj_site = Site.objects.all()[:1]
        obj_user = User()

        ctype_user = ContentType.objects.get_for_model(type(obj_user))
        ctype_site = ContentType.objects.get_for_model(type(obj_site[0]))

        item_user = self._create_item_in_db(content_object=self.user,
                                            quantity=1,
                                            unit_price=Decimal('100'))
        item_site = self._create_item_in_db(content_object=obj_site[0],
                                            quantity=2,
                                            unit_price=Decimal('100'))

        self.assertEquals(item_user.content_type, ctype_user)
        self.assertEquals(item_site.content_type, ctype_site)

        item_site.update_contenttype(self.user)
        self.assertEqual(item_site.content_object, self.user)
        self.assertEquals(item_site.quantity, 2)
        self.assertEquals(item_site.total_price, 200)

    def test_item_update_price(self):
        item = self._create_item_in_db(content_object=self.user)
        item.update_price(137)

        self.assertEquals(item.unit_price, 137)
