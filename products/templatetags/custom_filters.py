from django import template

register = template.Library()

@register.filter
def make_star_list(value):
    return [True] * value + [False] * (5 - value)



@register.filter(name='mul')
def mul(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        try:
            return int(value) * int(arg)
        except (ValueError, TypeError):
            return ''
        

@register.simple_tag
def subtract(a, b):
    return a - b