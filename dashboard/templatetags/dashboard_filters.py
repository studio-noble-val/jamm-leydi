"""
Custom template filters for dashboard
"""
from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Permet d'accéder aux valeurs d'un dictionnaire dans un template Django
    Usage: {{ dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
