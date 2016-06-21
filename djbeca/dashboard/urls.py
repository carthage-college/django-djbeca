from django.core.urlresolvers import reverse_lazy
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView, TemplateView

urlpatterns = patterns('djbeca.dashboard.views',
    # detailed view
    url(
        r'^proposal/(?P<pid>\d+)/detail/$',
        'proposal_detail', name="dashboard_proposal_detail"
    ),
    # proposal list
    url(
        r'^$', 'proposal_list', name="proposal_list"
    ),
)
