# -*- coding: utf-8 -*-

"""URLs for all views."""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include
from django.urls import path
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from djauth.views import loggedout
from djbeca.core import views


admin.autodiscover()

handler404 = 'djtools.views.errors.four_oh_four_error'
handler500 = 'djtools.views.errors.server_error'


urlpatterns = [
    # django admin
    path('rocinante/', include('loginas.urls')),
    path('rocinante/', admin.site.urls),
    # admin honeypot
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    # auth
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(),
        {'template_name': 'registration/login.html'},
        name='auth_login',
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(),
        {'next_page': reverse_lazy('auth_loggedout')},
        name='auth_logout',
    ),
    path(
        'accounts/loggedout/',
        loggedout,
        {'template_name': 'registration/logged_out.html'},
        name='auth_loggedout',
    ),
    path(
        'accounts/',
        RedirectView.as_view(url=reverse_lazy('auth_login')),
    ),
    path(
        'denied/',
        TemplateView.as_view(template_name='denied.html'),
        name='access_denied',
    ),
    # Proposal: Part A
    # -------------------------------------------------------------------------
    # Part A: new submission
    path('proposal/', views.proposal_form, name='proposal_form'),
    # Part A: Detail
    path(
        'proposal/<int:pid>/detail/',
        views.proposal_detail,
        name='proposal_detail',
    ),
    # Part A: update
    path(
        'proposal/<int:pid>/update/',
        views.proposal_form,
        name='proposal_update',
    ),
    path(
        'proposal/success/', views.proposal_success, name='proposal_success',
    ),
    # Proposal Impact: Part B
    # -------------------------------------------------------------------------
    # Part B: new submission
    path(
        'proposal/<int:pid>/impact/',
        views.impact_form,
        name='impact_form',
    ),
    path(
        'proposal/impact/success/', views.impact_success, name='impact_success',
    ),
    # Manager Dashboard
    # -------------------------------------------------------------------------
    # Assign approver to a proposal
    path(
        'proposal/<int:pid>/approver/',
        views.proposal_approver,
        name='proposal_approver',
    ),
    path(
        'proposal/approver/success/',
        views.approver_success,
        name='approver_success',
    ),
    path(
        'proposal/approver/',
        views.proposal_approver,
        name='proposal_approver_manager',
    ),
    # Send an email to primary investigator
    path(
        'proposal/email/success/',
        views.email_investigator_success,
        name='email_investigator_success',
    ),
    path(
        'proposal/email/<int:pid>/<str:action>/',
        views.email_investigator,
        name='email_investigator_form',
    ),
    # proposal status view for 'approve' or 'decline' actions
    path(
        'proposal/status/', views.proposal_status, name='proposal_status',
    ),
    # clear cache via ajax post
    path(
        'cache/<str:ctype>/clear/', views.clear_cache, name='clear_cache',
    ),
    # clear cache via GET
    path(
        'cache/clear/', views.clear_cache, name='clear_cache_get',
    ),
    # Home dashboard
    # -------------------------------------------------------------------------
    path('', views.home, name='home'),
]
