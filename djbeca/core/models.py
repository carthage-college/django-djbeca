# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models, connection
from django.contrib.auth.models import User


class Proposal(models.Model):
    """
    Proposal to pursue funding
    """
    user = models.ForeignKey(User)
    updated_by = models.ForeignKey(
        User,
        verbose_name="Updated by",
        related_name="proposal_updated_by",
        editable=False, null=True, blank=True
    )
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        "Date Updated", auto_now=True
    )
    title = models.CharField(
        "Proposal title", max_length=255
    )
    summary = models.TextField(
        "Proposal summary"
    )

    class Meta:
        ordering  = ['-created_at']
        get_latest_by = 'created_at'

    def __unicode__(self):
        """
        Default data for display
        """
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('proposal_detail', [str(self.id)])
