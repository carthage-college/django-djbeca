# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from djbeca.core.choices import *

from djtools.utils.users import in_group
from djtools.fields import BINARY_CHOICES
from djtools.fields.helpers import upload_to_path
from djtools.fields.validators import MimetypeValidator
from djzbar.utils.hr import chair_departments

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
    user = models.ForeignKey(User, editable=settings.DEBUG)
    # Division Dean or VP approval
    level3 = models.BooleanField(default=False)
    # anyone in the workflow decline the proposal at this point
    decline = models.BooleanField(default=False)
    # set to True when steps 1 & 2 have been approved by all and
    # post_save signal sends email to OSP
    email_approved = models.BooleanField(default=False)
    # PI has submitted proposal for final approval
    save_submit = models.BooleanField(default=False)
    # OSP will close a proposal when they have determined it is
    # over so that the PI can resubmit if they so choose
    closed = models.BooleanField(default=False)

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
    funding_agency_program_name = models.CharField(
        verbose_name="Funding Agency Name and Grant Program Name",
        max_length=128
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
    grant_agency_url = models.CharField(
        verbose_name="Solicitation Website",
        max_length=768,
    )
    grant_deadline_date = models.DateField(
        "Proposal Deadline Date"
    )
    # Investigator Information
    department = models.CharField(
        max_length=12
    )
    # NOTE: "Co-Principal Investigators & Associated Institution"
    # are ProposalContact() Foreign Key relationships.
    # Name, Instituion fields [limit 5]
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
        "Program summary (~500 words)",
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
    budget_total = models.DecimalField(
        "Total Budget Request",
        decimal_places=2,
        max_digits=16,
        help_text="List the total amount budgeted for this project"
    )
    budget_summary = models.TextField(
        "Budget Summary (~500 words)",
        help_text="Briefly describe your funding plan"
    )
    # additional comments
    comments = models.TextField(
        null=True, blank=True,
        help_text="Provide any additional comments if need be"
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

    def get_absolute_url(self):
        return 'https://{}{}'.format(
            settings.SERVER_URL,
            reverse('proposal_detail', args=(self.id,))
        )

    def get_update_url(self):
        return 'https://{}{}'.format(
            settings.SERVER_URL,
            #reverse('admin:core_proposal_change',args=(self.id,))
            reverse('proposal_update', args=(self.id,))
        )

    def get_slug(self):
        return 'proposal/'

    def permissions(self, user):
        '''
        what can the user access in terms of the proposal
        and viewing it and the approval process
        '''

        from djbeca.core.utils import get_position

        OSP_GROUP = settings.OSP_GROUP
        VEEP = get_position(settings.VEEP_TPOS)
        PROVOST = get_position(settings.PROV_TPOS)
        PRESIDENT = get_position(settings.PREZ_TPOS)

        perms = {
            'view':False,'approve':False,
            'superuser': False, 'approver': False,
            'level3': False, 'level2': False, 'level1': False
        }

        # in_group includes an exception for superusers
        group = in_group(user, OSP_GROUP)

        chair_depts = chair_departments(user.id)

        # dean or chair?
        dc = chair_depts[1]

        # Dean?
        if dc == 'dean':
            perms['view'] = True
            perms['level3'] = True
            perms['approve'] = 'level3'
        # Veep/CFO?
        elif user.id == VEEP.id:
            perms['view'] = True
            perms['level2'] = True
            perms['approve'] = 'level2'
        # Provost?
        elif user.id == PROVOST.id:
            perms['view'] = True
            perms['level1'] = True
            perms['approve'] = 'level1'
        # Superuser?
        elif group:
            perms['view'] = True
            perms['superuser'] = True
            perms['approve'] = 'superuser'
        elif self.user == user:
            perms['view'] = True
        # Ad-hoc approver?
        else:
            for a in self.proposal_approvers.all():
                if a.user == user:
                    perms['view'] = True
                    perms['approver'] = True
                    perms['approve'] = 'approver'
                    break

        return perms

    def impact(self):
        try:
            pi = self.proposal_impact
        except:
            pi = False
        return pi

    # at the moment, we assume all approvers will be responsible for
    # step 1 AND step 2. in the future, i suspect that this might change.
    def step1(self):
        approved = self.level3
        for a in self.proposal_approvers.all():
            if not a.step1:
                approved = False
                break
        return approved

    def step2(self):
        approved = False
        if self.proposal_impact.level1 and self.proposal_impact.level2 \
          and self.proposal_impact.level3:
            approved = True
        if approved:
            for a in self.proposal_approvers.all():
                if not a.step2:
                    approved = False
                    break
        return approved

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
    level3 = models.BooleanField(default=False) # Division Dean
    level2 = models.BooleanField(default=False) # CFO
    level1 = models.BooleanField(default=False) # Provost

    # Project Impact
    # NOTE: "Describe your project goal/s"
    # are ProposalGoal() Foreign Key relationships.
    # Name, Description fields [limit 8]

    # Strategic Plan Impact
    # HOLD ON DEVELOPING THIS SECTION: MAY ADD LATER

    # Institutional Impact
    cost_share_match = models.CharField(
        "Does this proposal require cost sharing/match?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    voluntary_committment = models.CharField(
        """
        Does this proposal contain any voluntary commitments
        on behalf of the College?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    subcontractors_subawards = models.CharField(
        """
        Does this proposal involve subcontracts and/or subawards
        with other institutions/organizations?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    students_involved = models.CharField(
        "Does this proposal involve the use of students?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    new_hires = models.CharField(
        "Does this proposal require any new faculty or staff hires?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    course_relief = models.CharField(
        """
        Does this proposal contain course relief of any Carthage personnel
        during the academic year?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    service_overload = models.CharField(
        """
        Does this proposal contain extra service or overload
        of any Carthage personnnel?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    irb_review = models.CharField(
        "Does this proposal require review of IRB?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    iacuc_review = models.CharField(
        "Does this proposal require review of IACUC?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    international = models.CharField(
        """
        Does this proposal involve international travel, collaboration,
        export, international student participation?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    hazards = models.CharField(
        """
        Does this proposal involve the use of chemical/physical hazards
        (including toxic or hazardous chemicals, radioactive material,
        biohazards, pathogens, toxins, recombinant DNA, oncongenic viruses,
        tumor cells, etc.)?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    proprietary_confidential = models.CharField(
        """
        Does this proposal involve work that may result in a patent
        or involve proprietary or confidential information?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    tech_support = models.CharField(
        """
        Does this proposal involve technology use that will require
        extensive technical support?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    purchase_equipment = models.CharField(
        """
        Does this proposal require any purchase, installation,
        and maintenance of equipment?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    infrastructure_requirements = models.CharField(
        """
        Does this proposal require any additional space than
        currently provided?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    disclosure_assurance = models.BooleanField(default=False)

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

    total = models.DecimalField(
        "Total budget request",
        decimal_places=2,
        max_digits=16,
        help_text="List the total amount budgeted for this project",
        null=True,blank=True
    )
    cost_match_amount = models.DecimalField(
        "Total Cost Share / Match Amount",
        decimal_places=2,
        max_digits=16,
        null=True,blank=True
    )
    # Files
    budget_final = models.FileField(
        "Final Budget for Review",
        upload_to=upload_to_path,
        #validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )
    budget_justification_final = models.FileField(
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


class ProposalDocument(models.Model):
    '''
    Proposal supporting documents
    '''
    # meta
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    proposal = models.ForeignKey(
        Proposal, editable=False,
        related_name='proposal_documents'
    )
    name = models.CharField(
        "Name or short description of the file",
        max_length=128,
        null=True,blank=True
    )
    phile = models.FileField(
        "Supporting Document",
        upload_to=upload_to_path,
        #validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format",
        null=True,blank=True
    )
    tags = TaggableManager(blank=True)

    class Meta:
        ordering  = ['-created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal_document'

    def get_slug(self):
        return 'proposal-document/'


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
        related_name='proposal_approvers'
    )
    # this field is not in use at the moment but i suspect
    # OSP will want to reactivate it in the future
    steps = models.CharField(
        max_length=4,
        default='3',
        choices=PROPOSAL_STEPS_CHOICES
    )
    replace = models.CharField(
        max_length=24,
        default='level3',
        choices=APPROVAL_LEVEL_CHOICES,
        null=True,blank=True
    )
    step1 = models.BooleanField(default=False)
    step2 = models.BooleanField(default=False)

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
