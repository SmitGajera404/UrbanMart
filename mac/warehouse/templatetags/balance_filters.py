from django import template

register = template.Library()

@register.filter
def format_balance(value):
    try:
        value = float(value)
        if value >= 1000000:
            return '{:.1f}M'.format(value / 1000000)
        elif value >= 1000:
            return '{:.1f}k'.format(value / 1000)
        else:
            return '{:.0f}'.format(value)
    except (ValueError, TypeError):
        return value
