from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

try:
    User = settings.AUTH_USER_MODEL
except (ImportError, AttributeError):
    from django.contrib.auth.models import User

try:
    from django.utils import timezone
except ImportError:
    from datetime import datetime as timezone


class BaseCart(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    creation_date = models.DateTimeField(verbose_name=_('creation date'),
                                         default=timezone.now)
    checked_out = models.BooleanField(default=False,
                                      verbose_name=_('checked out'))
    items = models.ManyToManyField('changuito.Item', related_name='cart',
                                   verbose_name=_('items'))

    class Meta:
        abstract = True
        verbose_name = _('cart')
        verbose_name_plural = _('carts')
        ordering = ('-creation_date',)
        app_label = 'changuito'

    def __unicode__(self):
        return 'Cart id: %s' % self.id

    def is_empty(self):
        return self.items.count() == 0

    def total_price(self):
        return sum(i.total_price for i in self.items.all())

    def total_quantity(self):
        return sum(i.quantity for i in self.items.all())


# To avoid extra DB table
class Cart(BaseCart):
    pass


class Item(models.Model):
    quantity = models.DecimalField(max_digits=18, decimal_places=3,
                                   verbose_name=_('quantity'))
    unit_price = models.DecimalField(max_digits=18, decimal_places=2,
                                     verbose_name=_('unit price'))
    # product as generic relation
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('items')
        ordering = ('cart',)
        app_label = 'changuito'

    def __unicode__(self):
        return u'{0} units of {1} {2}'.format(self.quantity,
                                              self.product.__class__.__name__,
                                              self.product.pk)

    def total_price(self):
        return float(self.quantity) * float(self.unit_price)
    total_price = property(total_price)

    def update_quantity(self, quantity):
        self.quantity = quantity
        self.save()

    def update_price(self, price):
        self.unit_price = price
        self.save()
