from django import template
register=template.Library()
@register.filter(name='get_val')
@register.filter(name='get_rating')
def get_val(dict, key):
    return dict.get(key)

@register.filter
def get_rating(value, max_rating):
    print(type(max_rating))
    return range(int(max_rating))
@register.filter
def minus(value, arg):
    print("inside ")
    try:
        return (value) - (arg)
    except (ValueError, TypeError):
        return 0