from django import template

from trax.trax import utils
register = template.Library()


@register.filter(name='humanize_timedelta')
def d(value):
    return utils.humanize_timedelta(value)
