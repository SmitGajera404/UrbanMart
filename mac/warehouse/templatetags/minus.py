from django import template
register=template.Library()

@register.filter(name='minus')
def minus(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0