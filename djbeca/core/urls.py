from django.core.urlresolvers import reverse_lazy
from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth import views as auth_views

from djauth.views import loggedout

from django.contrib import admin

admin.autodiscover()

handler404 = 'djtools.views.errors.four_oh_four_error'
handler500 = 'djtools.views.errors.server_error'

urlpatterns = patterns('djbeca.core.views',
    # Grappelli admin
    url(
        r'^grappelli/', include('grappelli.urls')
    ),
    # django admin
    url(
        r'^admin/', include(admin.site.urls)
    ),
    # auth
    url(
        r'^accounts/login/$',auth_views.login,
        {'template_name': 'accounts/login.html'},
        name='auth_login'
    ),
    url(
        r'^accounts/logout/$',auth_views.logout,
        {'next_page': reverse_lazy("auth_loggedout")},
        name="auth_logout"
    ),
    url(
        r'^accounts/loggedout/$',loggedout,
        {'template_name': 'accounts/logged_out.html'},
        name="auth_loggedout"
    ),
    url(
        r'^accounts/$',
        RedirectView.as_view(url=reverse_lazy("auth_login"))
    ),
    # redirect for portal decorator
    url(
        r'^denied/$',
        TemplateView.as_view(
            template_name="denied.html"
        ), name="access_denied"
    ),
    # proposal form
    url(
        r'^proposal/$',
        'proposal_form', name="proposal_form"
    ),
    url(
        r'^proposal/success/$',
        TemplateView.as_view(
            template_name='proposal/done.html'
        ),
        name='proposal_success'
    ),
    # proposal detail
    url(
        r'^proposal/(?P<pid>\d+)/detail/$',
        'proposal_detail', name="proposal_detail"
    ),
    # proposal_update
    #url(
        #r'^proposal/(?P<pid>\d+)/update/$',
        #'proposal_update', name="proposal_update"
    #),
    # approval form
    #url(
        #r'^proposal/(?P<pid>\d+)/approval/$',
        #'proposal_approval', name="proposal_approval"
    #),
    url(
        r'^proposal/approval/success/$',
        TemplateView.as_view(
            template_name='funding/approval/done.html'
        ),
        name='proposal_approval_success'
    ),
    # home
    url(
        r'^$', 'home', name="home"
    ),
)
