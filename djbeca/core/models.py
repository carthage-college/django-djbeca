# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from djbeca.core.choices import *

from djtools.fields import BINARY_CHOICES
from djtools.fields.helpers import upload_to_path
from djtools.fields.validators import MimetypeValidator

from taggit.managers import TaggableManager


class Proposal(models.Model):
    '''
    Proposal to pursue funding
    '''
    # meta
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        "Date Updated", auto_now=True
    )
    user = models.ForeignKey(User, editable=False)
    # status
    level2_approved = models.BooleanField(default=False) # division dean
    level1_approved = models.BooleanField(default=False) # provost
    # Basic Proposal Elements
    proposal_type = models.CharField(
        "What type of proposal submission is this?",
        max_length=128,
        choices=PROPOSAL_TYPE_CHOICES,
    )
    proposal_type_other = models.CharField(
        "If 'Other', please provide details",
        max_length=128,
        null=True,blank=True
    )
    grant_agency_name = models.CharField(
        verbose_name="Grant Agency and Program Name",
        max_length=128,
    )
    grant_agency_funding_source = models.CharField(
        verbose_name="What type of funding source is the granting agency?",
        max_length=128,
        choices=FUNDING_SOURCE_CHOICES,
    )
    grant_agency_funding_other = models.CharField(
        "If 'Other', please provide details",
        max_length=128,
        null=True,blank=True
    )
    grant_name = models.CharField(
        verbose_name="Name of Grant / Specific Funding Opportunity",
        max_length=128,
    )
    grant_agency_url = models.CharField(
        verbose_name="Solicitation Website",
        max_length=768,
    )
    grant_deadline_date = models.DateField(
        "Proposal Deadline Date"
    )
    grant_deadline_time = models.TimeField(
        "Proposal Deadline Time",
        #input_formats=('%I:%H %p',)
    )
    # Investigator Information
    # NOTE: we have name, email, ID from user profile data
    phone = models.CharField(
        verbose_name='Phone',
        max_length=12,
        help_text="Format: XXX-XXX-XXXX"
    )
    department = models.CharField(
        max_length=12
    )
    # NOTE: "Co-Principal Investigators & Associated Institution"
    # are ProposalContact() Foreign Key relationships.
    # Name, Instituion fields [limit 5]
    partner_institutions = models.CharField(
        "Are other institutions involved?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    # NOTE: "List all institutions involved"
    # are ProposalContact() FK relationships.
    # Name field [limit 5]
    lead_institution = models.CharField(
        "Is Carthage College the lead institution on this project?",
        max_length=4,
        choices=BINARY_CHOICES,
        null=True,blank=True
    )
    # NOTE: if 'No', provide the following
    lead_institution_name = models.CharField(
        "Name of lead institution",
        max_length=128,
        null=True,blank=True
    )
    lead_institution_contact = models.TextField(
        "Lead institution contact information",
        help_text = "Sponsored Programs Office (or equivalent)",
        null=True,blank=True
    )
    # Project Overview
    title = models.CharField(
        "Project title", max_length=255
    )
    start_date = models.DateField("Project start date")
    end_date = models.DateField("Project end date")
    project_type = models.CharField(
        max_length=128,
        choices=PROJECT_TYPE_CHOICES,
    )
    summary = models.TextField(
        "Program summary (~250 words)",
        help_text="""
            Provide a brief description of your proposed project
            and how the proposed project addresses one or more
            strategies/goals in Carthage’s strategic plan.
        """
    )
    # Project Funding / Budget Overview
    time_frame = models.CharField(
        "Is this one year funding or multi-year?",
        max_length=128,
        choices=TIME_FRAME_CHOICES
    )
    budget_total = models.CharField(
        "Total Budget Request",
        max_length=16,
        help_text="List the total amount budgeted for this project"
    )
    funding_plan = models.TextField(
        "Funding Plan (~250 words)",
        help_text="""
            Briefly describe your funding plan/s for any project budget
            costs in excess of the proposal request.
        """
    )

    class Meta:
        ordering  = ['-created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal'

    def __unicode__(self):
        '''
        Default data for display
        '''
        return "{} ({})".format(self.title, self.id)

    @models.permalink
    def get_absolute_url(self):
        return ('proposal_detail', [str(self.id)])

    def get_update_url(self):
        return 'https://{}{}'.format(
            settings.SERVER_URL,
            reverse('admin:core_proposal_change',args=(self.id,))
            #reverse('proposal_update',args=(self.id,))
        )

    def get_slug(self):
        return 'proposal/'


class ProposalImpact(models.Model):
    '''
    Proposal impacts
    '''
    # meta
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        "Date Updated", auto_now=True
    )
    proposal = models.OneToOneField(
        Proposal, editable=False,
        related_name='proposal_impact'
    )

    # status
    level2_approved = models.BooleanField(default=False) # division dean
    level1_approved = models.BooleanField(default=False) # provost

    # Project Impact
    # NOTE: "Describe your project goal/s"
    # are ProposalGoal() Foreign Key relationships.
    # Name, Description fields [limit 8]

    # Strategic Plan Impact
    # HOLD ON DEVELOPING THIS SECTION: MAY ADD LATER

    # Institutional Impact
    course_release = models.CharField(
        "Does this proposal require course release or overload?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    additional_pay = models.CharField(
        "Does this proposal require additional pay?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    payout_students = models.CharField(
        "Does this proposal require payout to Carthage students?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    new_positions = models.CharField(
        "Does this proposal require the creation of new Carthage positions?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    purchase_equipment = models.CharField(
        """
            Does this proposal result in the purchase of major equipment,
            costing over $5,000?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    infrastructure_modifications = models.CharField(
        """
            Does this proposal require additional office,
            lab or other facilities or room modifications?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    institutional_review = models.CharField(
        "Does this proposal require review of IRB and/or IACUC?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    institutional_review_date = models.DateField(
        "If 'Yes', please provide the approval date",
        null=True,blank=True
    )
    cost_share_match = models.CharField(
        "Does this proposal require cost share/match?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    voluntary_committment = models.CharField(
        "Does this proposal contain any voluntary commitment?",
        max_length=4,
        choices=BINARY_CHOICES,
        help_text = "e.g. faculty/staff time, cost share/match"
    )

    class Meta:
        ordering  = ['-created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal_impact'

    def get_slug(self):
        return 'proposal-impact/'


class ProposalBudget(models.Model):
    '''
    Proposal budget
    '''
    # meta
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        "Date Updated", auto_now=True
    )
    proposal = models.OneToOneField(
        Proposal, editable=False,
        related_name='proposal_budget'
    )
    # Costs and totals
    total = models.CharField(
        "Total budget request",
        max_length=16,
        help_text="List the total amount budgeted for this project",
        null=True,blank=True
    )
    cost_match_amount = models.CharField(
        "Total Cost Share / Match Amount",
        max_length=16,
        null=True,blank=True
    )
    indirect_cost = models.CharField(
        "Total Indirect Costs Requested",
        max_length=16,
        null=True,blank=True
    )
    indirect_cost_rate = models.CharField(
        "What is Indirect Cost Rate Used?",
        max_length=128,
        choices=INDIRECT_COST_RATE_CHOICES,
        null=True,blank=True
    )
    indirect_cost_rate_other = models.CharField(
        "If 'Other', please specify the rate",
        max_length=128,
        null=True,blank=True
    )
    # Files
    document = models.FileField(
        "Final Budget for Review",
        upload_to=upload_to_path,
        #validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )
    overview = models.FileField(
        "Final Budget Justification for Review",
        upload_to=upload_to_path,
        #validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format",
        null=True,blank=True
    )

    class Meta:
        ordering  = ['-created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal_budget'

    def get_slug(self):
        return 'proposal-budget/'


class ProposalContact(models.Model):
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    proposal = models.ForeignKey(
        Proposal,
        editable=False,
        related_name='proposal_contact'
    )
    name = models.CharField(
        max_length=128,
        null=True, blank=True
    )
    institution = models.CharField(
        max_length=128,
        null=True, blank=True
    )
    email =  models.EmailField(
        "Your email address",
        max_length=128,
        null=True, blank=True
    )
    tags = TaggableManager(blank=True)

    class Meta:
        ordering = ['institution']
        #ordering  = ['-created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal_contact'

    def get_slug(self):
        return 'proposal-contact/'

    def __unicode__(self):
        return u'{}: {}'.format(self.name, self.institution)


class ProposalGoal(models.Model):
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    proposal = models.ForeignKey(
        Proposal,
        editable=False,
        related_name='proposal_goal'
    )
    name = models.CharField(
        max_length=128,
        null=True, blank=True,
        choices=PROPOSAL_GOAL_CHOICES
    )
    description = models.TextField(
        null=True, blank=True,
        help_text="~200 words"
    )

    class Meta:
        ordering = ['institution']

    def __unicode__(self):
        return u'{}: {}'.format(self.name, self.institution)


    class Meta:
        ordering  = ['-created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal_goal'

    def get_slug(self):
        return 'proposal-goal/'

    def __unicode__(self):
        return u'{}'.format(self.name)


class ProposalApprover(models.Model):
    '''
    Additional folks who need to approve a proposal
    '''
    user = models.ForeignKey(
        User,
        related_name='approver_user'
    )
    proposal = models.ForeignKey(
        Proposal,
        related_name='approver'
    )
    steps = models.CharField(
        max_length=4,
        default='0',
        choices=PROPOSAL_STEPS_CHOICES
    )
    approved = models.BooleanField(default=False)

    class Meta:
        db_table = 'core_proposal_approver'

    def first_name(self):
        return self.user.first_name

    def last_name(self):
        return self.user.last_name

    def email(self):
        return self.user.email

    def title(self):
        return self.proposal.title
