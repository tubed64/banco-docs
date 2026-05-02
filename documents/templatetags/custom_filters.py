from django import template

register = template.Library()


@register.filter
def replace(value, args):
    """
    Reemplaza un string por otro en un valor.
    Uso en template: {{ value|replace:"old:new" }}
    """
    if not args or ':' not in args:
        return value
    
    old, new = args.split(':', 1)
    return str(value).replace(old, new)
