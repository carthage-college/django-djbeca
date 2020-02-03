# -*- coding: utf-8 -*-

"""Views for all requests."""

from django.conf import settings


def sitevars(request):
    """Expose some settings to the template level."""
    context = {}
    context['osp_group'] = settings.OSP_GROUP
    context['deans_group'] = settings.DEANS_GROUP

    return context
