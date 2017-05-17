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
    department_approved = models.BooleanField(default=False)
    division_approved = models.BooleanField(default=False)
    provost_approved = models.BooleanField(default=False)
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
        verbose_name="Grant Agency Solicitation URL",
        max_length=768,
    )
    grant_deadline_date = models.DateField(
        "Proposal Deadline Date"
    )
    grant_deadline_time = models.TimeField(
        "Proposal Deadline Time",
        help_text="(Format HH:MM am/pm)"
    )
    proposal_submission_entity = models.CharField(
        "Who is required to submit the final submission?",
        max_length=128,
        choices=PROPOSAL_SUBMISSION_ENTITY_CHOICES
    )
    proposal_submission_entity_other = models.CharField(
        "If 'Other', please list names",
        max_length=128,
        null=True,blank=True
    )
    proposal_submission_method = models.CharField(
        "How is the proposal to be submitted?",
        max_length=128,
        choices=PROPOSAL_SUBMISSION_METHOD_CHOICES,
    )
    proposal_submission_method_other = models.CharField(
        "If 'Other', please provide details",
        max_length=128,
        null=True,blank=True
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
    # are GenericContact() Foreign Key relationships.
    # Name, Instituion fields [limit 5]
    partner_institutions = models.CharField(
        "Are other institutions involved?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    # NOTE: "List all institutions involved"
    # are GenericContact() FK relationships.
    # Name field [limit 5]
    lead_institution = models.CharField(
        "Is Carthage College the lead institution on this project?",
        max_length=4,
        choices=BINARY_CHOICES,
        null=True,blank=True
    )
    # NOTE: if 'No', GenericContact() FK relationship.
    # Name, Institution, email
    partner_institution = models.CharField(
        "Name of Partner Institution(s)",
        max_length=128,
        null=True,blank=True
    )
    partner_institution_contact = models.TextField(
        "Partner Institution(s) contact information",
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
    # Project Funding/ Budget Overview
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
    funding_total = models.CharField(
        """
            List the total amount of funding you intend
            to request through this proposal
        """,
        max_length=16,
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
        return self.title

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
    proposal = models.ForeignKey(
        Proposal, editable=False,
        related_name='project_impact'
    )

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
        help_text = "(ex: faculty/staff time, cost share/match)"
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
    proposal = models.ForeignKey(
        Proposal, editable=False,
        related_name='project_budget'
    )
    # core
    document = models.FileField(
        "Completed budget",
        upload_to=upload_to_path,
        validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )
    overview = models.TextField(
        "Budget Overview/Narrative",
        help_text="~1000 words",
        null=True,blank=True
    )
    total = models.CharField(
        "Total budget request",
        max_length=16,
        help_text="List the total amount budgeted for this project",
        null=True,blank=True
    )
    # Annual Budget Breakout
    year_1 = models.CharField(
        "Year 1",
        max_length=16,
        null=True,blank=True
    )
    year_2 = models.CharField(
        "Year 2",
        max_length=16,
        null=True,blank=True
    )
    year_3 = models.CharField(
        "Year 3",
        max_length=16,
        null=True,blank=True
    )
    year_4 = models.CharField(
        "Year 4",
        max_length=16,
        null=True,blank=True
    )
    year_5 = models.CharField(
        "Year 5",
        max_length=16,
        null=True,blank=True
    )
    # indirect costs
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
    # Cost Share / Match
    cost_match_required = models.CharField(
        "Is a cost share/ match required?",
        max_length=4,
        choices=BINARY_CHOICES,
    )

    class Meta:
        ordering  = ['-created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal_budget'

    def get_slug(self):
        return 'proposal-budget/'


class GenericContact(models.Model):
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    proposal = models.ForeignKey(
        Proposal,
        editable=False,
        related_name='generic_contact'
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
    tags = TaggableManager()

    class Meta:
        ordering = ['institution']
        #ordering  = ['-created_at']
        get_latest_by = 'created_at'
        db_table = 'core_generic_contact'

    def get_slug(self):
        return 'generic-contact/'

    def __unicode__(self):
        return u'{}: {}'.format(self.name, self.institution)


class ProposalGoal(models.Model):
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    proposal_impact = models.ForeignKey(
        ProposalImpact,
        editable=False,
        related_name='proposal_impact_goal'
    )
    name = models.CharField(
        max_length=128,
        null=True, blank=True
    )
    description = models.TextField(
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

