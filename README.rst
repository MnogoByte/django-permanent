django-ordered-listview
=======================

About
-----

This library is aimed to simplify creation of user sorted lists.
Inspired by https://gist.github.com/piquadrat/3833430

Installation
------------

1. Install with pip or setup.py

2. Add ordered_listview into `INSTALLED_APPS`. ::

    INSTALLED_APPS += ['ordered__listview']

3. Add template tags lib into builtins. ::

    add_to_builtins('ordered_listview.templatetags.ordered_listview')  // Or load with {% load ordered_listview %}

4. Inherit your view from `OrderedListView`. And setup your ordering fields. ::

    from ordered_listview import OrderedListView

    class UserListView(OrderedListView):
        allowed_order_by = [
            ('username', _('Login')),
            ('userfile__file__size', _('Size')),
            ('date_joined', _('Sing up date'))
        ]
        default_order_by = 'created'

5. Add a tag into you your template. ::

    {% include "ordered_listview/fields.html" %}


Customization
-------------

1. To change get attribute name, just set `OrderedListView.order_by` attribute ::

    class UserListView(OrderedListView):
        order_by = "order_by"

2. If you need to provide your own template create inside your `templates`
`ordered_listview` directory with `fields.html` and `field.html` in.

    fields.html - list of sortable fields
    field.html - order field and state template
