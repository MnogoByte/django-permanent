from django.conf import settings


FIELD_CLASS = getattr(settings, 'PERMANENT_FIELD_CLASS', 'django.db.models.DateTimeField')
FIELD = getattr(settings, 'PERMANENT_FIELD', 'removed')
FIELD_KWARGS = getattr(settings, 'PERMANENT_FIELD_KWARGS', dict(
    default=None,
    null=True,
    blank=True,
    editable=False
))

FIELD_DEFAULT = FIELD_KWARGS['default']
