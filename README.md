django-changuito
=================

[![Build Status](https://travis-ci.org/angvp/django-changuito.png)](https://travis-ci.org/angvp/django-changuito)
[![Coverage Status](https://coveralls.io/repos/angvp/django-changuito/badge.svg?branch=master&service=github)](https://coveralls.io/github/angvp/django-changuito?branch=master)


# Introduction

django-changuito, is a simple cart based on django-cart, it allows you to have
a session cart for logged and not logged users, it's born from the need of features
that weren't available on django-cart and the previous main developer seems to
doesn't have more free time, we are very thankful for his work but we don't
want to maintain our own version of django-cart, so we forked and did our changes
and make everything open source on a public repo and uploaded to PyPI.

We are already using it on production and we want to encourage old users
of django-cart or forked projects of django-cart to migrate to changuito instead.

## Prerequisites

- Django 1.7, 1.8, 1.9, 1.10, 1.11, 2.0.7
- Python 2.7 and Python 3.4+
- django content type framework in your INSTALLED_APPS

## Installation

To install this just type:

```
python setup.py install
```

or actually, until possible merge with django-changuito or upload to PyPI:

```
pip install git+https://github.com/txerpa/django-changuito.git@master
```

## Testing

You need to install Sqlite3 and requirements in `requirements-test.txt`

For running the test suite please do:

```
python runtests.py
```

Or simply run `tox` (if you want to test all the envs)

After installation is complete:

1. Add `changuito` to your INSTALLED_APPS directive
2. Make migrations `./manage.py makemigrations changuito`
3. Syncronize the DB: `./manage.py migrate changuito`

## Usage

A basic usage of django-changuito could be (example):

```python
#settings.py
MIDDLEWARE_CLASES += ('changuito.middleware.CartMiddleware', )
```


```python
# views.py
from my_shop.models import Product

def add_to_cart(request, product_id, quantity=1):
    product = Product.objects.get(id=product_id)
    cart = request.cart 
    cart.add_item(product, product.unit_price, quantity)

def remove_from_cart(request, item_id):
    cart = request.cart 
    cart.remove_item(item_id)

def get_cart(request):
    return render_to_response('cart.html', dict(cart=CartProxy(request)))
```

```django
# templates/cart.html
{% extends 'base.html' %}

{% block body %}
    <table>
        <tr>
            <th>Product</th>
            <th>Description</th>
            <th>Quantity</th>
            <th>Total Price</th>
        </tr>
        {% for item in cart %}
        <tr>
            <td>{{ item.content_object.name }}</td>
            <td>{{ item.content_object.description }}</td>
            <td>{{ item.quantity }}</td>
            <td>{{ item.total_price }}</td>
        </tr>
        {% endfor %}
    </table>
{% endblock %}
```

## Customize your cart

If you need a cart with more attributes you have to do the following:

```python
#settings.py
CART_MODEL = 'my_shop.Cart'
```

```python
#models.py
from changuito.models import BaseCart

class Cart(BaseCart):
    transaction_id = models.CharField(max_length=50, blank=True)

    class Meta:
        # To ensure that the DB table is created for your app
        db_table = 'my_shop_cart'
```

Finally:
- Make migrations: `./manage.py makemigrations changuito`
- Syncronize the DB: `./manage.py migrate my_shop`


NOTE: If you define `CART_MODEL` changuito's initial migration will not create its default `Cart` model.
Then we recommend to migrate after have defined it to avoid create an unnecessary DB table.

NOTE2: If you need a special checkout or extra behavior you only have to inherit from `CartProxy`
and overwrite it. Then you will have to create your own middleware that uses your new proxy.


## Some Info

This is from the original project that I've forked, I just renamed the project since
is not officialy dead and continued my work on this project.

```
This project was abandoned and I got it and added tests and South migrations, 
and I will be maintaining it from now on. 
```

## A note on the authors of this project

This project is a fork of django-cart which was originally started by Eric Woudenberg and followed up by Marc Garcia <http://vaig.be>, and then continued by Bruno Carvalho, which adds a lot of stuff and then wasn't much aware of the status of the project.
The last change ocurred in Jan 29 2012. Bruno and other authors added tests and cool stuff and we are thankful for that, and we will continue with that spirit.


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/angvp/django-changuito/trend.png)](https://bitdeli.com/free "Bitdeli Badge")
