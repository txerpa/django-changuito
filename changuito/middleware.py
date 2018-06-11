from .proxy import CartProxy

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


class CartMiddleware(MiddlewareMixin):

    def process_request(self, request):

        # You can't modify the session if the requested view has csrf protection
        if 'csrfmiddlewaretoken' not in request.POST:
            request.cart = CartProxy(request)
