from django.urls import reverse
from django.utils.html import format_html


def get_admin_url(obj):
    url_name = 'admin:{0}_{1}_change'.format(obj._meta.app_label, obj._meta.model_name)
    return reverse(url_name, args=[obj.pk])


def get_admin_link(obj, name=None):
    if not obj:
        return '-'
    link_name = name or str(obj)
    return format_html('<a href="{0}">{1}</a>', get_admin_url(obj), link_name)


def get_admin_links(objects):
    if not objects:
        return '-'

    links = []
    for obj in objects:
        # Each objects link name will be its __str__()
        links.append(f'<a href="{get_admin_url(obj)}">{obj}</a>')
    return format_html(', '.join(links))
