from django import template

register = template.Library()

@register.filter(name='format_md_tuple')
def format_md_tuple(md_tuple):
    if isinstance(md_tuple, tuple) and len(md_tuple) == 2:
        year, month = md_tuple
        return f"{year}/{month}"
    else:
        year, month, day = md_tuple
        return f"{year}/{month}/{day}"

@register.filter(name='format_sales_data')
def format_sales_data(sales_data):
    formatted_data = []
    for fruit, details in sales_data.items():
        formatted_data.append(f"{fruit}: {details['amount']}円 ({details['quantity']})")
    return '   '.join(formatted_data)
