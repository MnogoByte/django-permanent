# -*- coding: utf-8 -*-
from django.conf import settings


PERMANENT_FIELD = getattr(settings, 'PERMANENT_FIELD', 'removed')
