from django import template

register = template.Library()

@register.filter
def float_to_css_width(value):
    try:
        f = float(value)   # <-- définir la variable f ici
        if f < 0:
            f = 0
        elif f > 100:
            f = 100
        # Forcer le point décimal
        return "{0:.2f}".format(f).replace(',', '.')
    except (ValueError, TypeError):
        return "0.00"
