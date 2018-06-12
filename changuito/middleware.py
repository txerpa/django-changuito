# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from .proxy import CART_ID, CartProxy


class CartMiddleware(object):

    def process_request(self, request):

        # You can't modify the session if the requested view has csrf protection
        if 'csrfmiddlewaretoken' not in request.POST:
            request.cart = CartProxy(request)
            request.session[CART_ID] = request.cart.cart.id
