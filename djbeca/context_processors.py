from django.conf import settings

def sitevars(request):
    context = {}
    context['osp_group'] = settings.OSP_GROUP
    context['deans_group'] = settings.DEANS_GROUP

    return context
