# -*- coding: utf-8 -*-

"""Views for all requests."""

from django.conf import settings
from djtools.utils.workday import get_deans


def sitevars(request):
    """Expose some settings to the template level."""
    user = request.user
    context = {}
    context['osp'] = user.groups.filter(name=settings.OSP_GROUP).exists()
    for dean in get_deans():
        if request.user.id == dean['id']:
            context['dean'] = True
            break
    return context
