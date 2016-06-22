# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models, connection
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class Proposal(models.Model):
    """
    Proposal to pursue funding
    """

    user = models.ForeignKey(User, editable=False)
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        "Date Updated", auto_now=True
    )
    department = models.CharField(
        max_length=12
    )
    title = models.CharField(
        "Proposal title", max_length=255
    )
    summary = models.TextField(
        "Proposal summary"
    )
    funding = models.BooleanField(
        "Do you have a funding source?",
        help_text="Check the box if you have found a funding source",
        default=False
    )
    department_approved = models.BooleanField(default=False)
    division_approved = models.BooleanField(default=False)
    email_approved = models.BooleanField(default=False)

    class Meta:
        ordering  = ['-created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal'

    def __unicode__(self):
        """
        Default data for display
        """
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('dashboard_proposal_detail', [str(self.id)])

    def get_update_url(self):
        return "https://{}{}".format(
            settings.SERVER_URL, reverse('admin:core_proposal_change',args=(self.id,))
        )

'''
class Funding(models.Model):
    """
    Funding source(s) for proposal
    """
    proposal = ForeignKey(Proposal, null=True, blank=True)
'''

