from django.dispatch import Signal

pre_restore = Signal(providing_args=['instance'])
post_restore = Signal(providing_args=['instance'])
