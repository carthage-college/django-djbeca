# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models, connection
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from djbeca.core.choices import *

from djtools.fields import BINARY_CHOICES


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
        "Program title", max_length=255
    )
    summary = models.TextField(
        "Program summary (~1000 characters)",
        help_text="""
            Provide a brief description of your proposed project
            and how the proposed project addresses one or more
            strategies/goals in Carthage’s strategic plan.
        """
    )
    funding_status = models.CharField(
        max_length=128,
        choices=FUNDING_CHOICES
    )
    department_approved = models.BooleanField(default=False)
    division_approved = models.BooleanField(default=False)
    status = models.BooleanField(
        "Will not pursue at this time",
        default=False
    )
    email_approved = models.BooleanField(default=False)

    class Meta:
        ordering  = ['-created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal'

    def __unicode__(self):
        '''
        Default data for display
        '''
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('dashboard_proposal_detail', [str(self.id)])

    def get_update_url(self):
        return 'https://{}{}'.format(
            settings.SERVER_URL,
            reverse('admin:core_proposal_change',args=(self.id,))
        )


class FundingPursued(models.Model):
    '''
    Pursuit of Funding source(s) for proposal
    '''
    proposal = models.ForeignKey(
        Proposal,
        related_name="funding_pursued",
    )
    budget_information = models.CharField(
        max_length=128
    )
    amount_required = models.DecimalField(
        max_digits=8, decimal_places=2,
        help_text="In dollars"
    )
    project_duration = models.TextField(
        help_text="""
            What is your funding time line?
            How soon will you require funding? (~500 characters)
        """
    )
    project_end = models.CharField(
        "At the end of the project, it will",
        max_length=128,
        choices=PROJECT_END_CHOICES,
    )


class FundingIdentified(models.Model):
    '''
    Identified Funding source(s) for proposal
    '''
    proposal = models.ForeignKey(
        Proposal,
        related_name="funding_identified",
    )
    # Funding Identified
    classification = models.CharField(
        "Would this proposal classify Carthage as a",
        max_length=128,
        choices=CLASSIFICATION_CHOICES,
    )
    partner = models.CharField(
        "Does this proposal partner with another institution?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    partner_institution = models.CharField(
        "Name of Partner Institution",
        max_length=128,
        null=True,blank=True
    )
    co_partner_institution = models.CharField(
        "Name of Co-Partner Institution(s)",
        max_length=255,
        null=True,blank=True
    )
    partner_institution_contact = models.TextField(
        "Institution Sponsored Programs Office contact name and information",
        null=True,blank=True
    )
    # Sponsor Information
    sponsor_agency_name = models.CharField(
        max_length=128,
    )
    sponsor_funding_name = models.CharField(
        "Sponsor Funding Opportunity Name",
        max_length=128,
    )
    sponsor_deadline_date = models.DateField()
    sponsor_url = models.CharField(
        "Sponsor web address/link to solicitation",
        max_length=128,
    )
    sponsor_time_frame = models.CharField(
        "Please choose the time frame",
        max_length=128,
        choices=TIME_FRAME_CHOICES,
    )
    sponsor_type = models.CharField(
        max_length=128,
        choices=SPONSOR_TYPE_CHOICES,
    )
    # Proposal and Budget Information
    start_date = models.DateField("Project start date")
    end_date = models.DateField("Project end date")
    amount_required = models.DecimalField(
        max_digits=8, decimal_places=2,
        help_text="In dollars"
    )
    match_required = models.CharField(
        "Cost Match Requirement",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    match_description = models.TextField(
        """
            If yes, please describe any cost match funding and
            cost match requirements such as amount/percentage
        """,
        null=True,blank=True
    )
    support_facstaff = models.CharField(
        "Will funds support faculty/staff devoted to project?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    support_facstaff_info = models.TextField(
        "If yes, please provide the following per individual:",
        help_text = mark_safe(
            """
            <ul class="ul-block">
              <li>Name</li>
              <li>
                Devoted to activity in summer months, academic year, or both
              </li>
              <li>Percentage of time devoted to project</li>
              <li>Percentage of time charged to sponsor</li>
            </ul>
            """
        ),
        null=True,blank=True
    )
    activity_term = models.CharField(
        max_length=128,
        choices=TERM_CHOICES,
    )
    partner_participation = models.CharField(
        """
            Partner Institution will devote the following percent
            of the total academic year effort to the project
        """,
        max_length=2
    )
    sponsor_participation = models.CharField(
        """
            Sponsor will be charged the following percent of the
            above Partner Institution's effort
        """,
        max_length=2
    )
    undergraduates = models.CharField(
        "Will funds support undergraduates",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    undergraduates_number = models.IntegerField(
        "If yes, indicate the approximate number",
        null=True,blank=True
    )
    undergraduates_carthage = models.IntegerField(
        "How many of these are Carthage undergraduates?",
        null=True,blank=True
    )
    room_board = models.CharField(
        "Will Carthage room and board be needed?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    room_board_number = models.IntegerField(
        null=True,blank=True
    )
    # Institutional Impact
    course_release = models.CharField(
        "Will this proposal require course release or overload?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    course_release_details = models.TextField(
        "If so, please provide details",
        null=True,blank=True
    )
    new_personnel = models.CharField(
        "Will this proposal require hiring of new personnel?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    new_personnel_details = models.TextField(
        "If so, please provide details",
        null=True,blank=True
    )
    major_equipment = models.CharField(
        """
            Will this proposal result in purchase of major equipment,
            including computers and software, or renovations?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    major_equipment_details = models.TextField(
        "If so, please provide details",
        null=True,blank=True
    )

