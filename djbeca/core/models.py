# -*- coding: utf-8 -*-

"""Data models."""

from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from djbeca.core import choices
from djimix.people.departments import chair_departments
from djtools.fields.helpers import upload_to_path
from djtools.utils.users import in_group
from taggit.managers import TaggableManager


ALLOWED_EXTENSIONS = ['xls', 'xlsx', 'pdf']
FILE_VALIDATORS = [
    FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS),
]


def limit_subcontracts():
    """Return choices for m2m field in ProposalImpact data model."""
    ids = [
        choice.id for choice in GenericChoice.objects.filter(
            tags__name__in=['Subcontracts'],
        ).order_by('rank')
    ]
    return {'id__in': ids}


class GenericChoice(models.Model):
    """Choices for model and form fields that accept for multiple values."""

    name = models.CharField(max_length=255)
    value = models.CharField(unique=True, max_length=255)
    rank = models.IntegerField(
        verbose_name="Ranking",
        null=True,
        blank=True,
        default=0,
        help_text="A number that determines this object's position in a list.",
    )
    active = models.BooleanField(
        help_text="""
            Do you want the field to be visable on the public submission form?
        """,
        verbose_name="Is active?",
        default=True,
    )
    admin = models.BooleanField(
        verbose_name="Administrative only", default=False,
    )
    tags = TaggableManager(blank=True)

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['rank']

    def __str__(self):
        """Default data for display."""
        return self.name


class Proposal(models.Model):
    """Proposal to pursue funding."""

    # meta
    created_at = models.DateTimeField('Date Created', auto_now_add=True)
    updated_at = models.DateTimeField('Date Updated', auto_now=True)
    user = models.ForeignKey(
        User,
        editable=settings.DEBUG,
        on_delete=models.CASCADE,
    )
    # Division Dean or Department VP approval
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
    # signifies that it has been reopened
    opened = models.BooleanField(default=False)
    # signifies that it has been awarded funds
    awarded = models.BooleanField(default=False)

    # Basic Proposal Elements
    proposal_type = models.CharField(
        "What type of proposal submission is this?",
        max_length=128,
        choices=choices.PROPOSAL_TYPE_CHOICES,
        help_text=mark_safe(
            """
            <ul class='block'>
            <li>
              <b>New</b>: never submitted this proposal to this agency before
            </li>
            <li>
              <b>Revised</b>: per Funder Request: update of submitted proposal,
              because funder requested changes
            </li>
            <li>
              <b>Re-Submission</b>: submitted proposal in prior round of
              funding, re-submitting proposal for new round
            </li>
            </ul>
        """,
        ),
    )
    proposal_type_other = models.CharField(
        "If 'Other', please provide details",
        max_length=128,
        null=True,
        blank=True,
    )
    funding_agency_program_name = models.CharField(
        "Funding/Sponsor Agency Name and Grant Program Name",
        max_length=128,
    )
    grant_agency_funding_source = models.CharField(
        "What type of funding source is the granting agency?",
        max_length=128,
        choices=choices.FUNDING_SOURCE_CHOICES,
    )
    grant_agency_funding_source_other = models.CharField(
        "If 'Other', please provide details",
        max_length=128,
        null=True,
        blank=True,
    )
    grant_agency_url = models.CharField("Solicitation Website", max_length=512)
    grant_deadline_date = models.DateField("Proposal Deadline Date")
    # Investigator Information
    department = models.CharField(max_length=12)
    """
    NOTE "Co-Principal Investigators & Associated Institution"
    are ProposalContact() Foreign Key relationships.
    Name, Instituion fields [limit 5]
    """
    lead_institution = models.CharField(
        "In this proposal, Carthage is considered:",
        max_length=24,
        choices=choices.LEAD_INSTITUTION_CHOICES,
        null=True,
        blank=True,
    )
    lead_institution_contact = models.TextField(
        "Lead institution contact information",
        help_text="Sponsored Programs Office (or equivalent)",
        null=True,
        blank=True,
    )
    # Project Overview
    title = models.CharField("Project title", max_length=255)
    start_date = models.DateField("Project start date")
    end_date = models.DateField("Project end date")
    project_type = models.CharField(
        max_length=128,
        choices=choices.PROJECT_TYPE_CHOICES,
    )
    project_type_other = models.CharField(
        "If 'Other', please provide details",
        max_length=128,
        null=True,
        blank=True,
    )
    summary = models.TextField(
        "Program summary (~500 words)",
        help_text="""
            Provide a brief description of your proposed project.
            How does your project help further Carthage's mission?
            Describe any partnerships or collaborative relationships
            needed to execute the project. 
        """,
    )
    # Project Funding / Budget Overview
    budget_total = models.DecimalField(
        "Total Program Cost",
        decimal_places=2,
        max_digits=16,
        help_text="List the total amount budgeted for this project",
    )
    budget_summary = models.TextField(
        "Budget Summary (~500 words)",
        help_text=mark_safe(
        """
            Describe your funding plan: 
            <ul>
                <li>
                    What types of expenses do you expect to have
                    (summer salary, travel, student research dollars,
                    admin support, materials and supplies, equipment,
                    etc...)?
                </li>
                <li>
                    Will this grant provide new funds for a new project
                    or new funds for an existing project? Will the grant
                    provide any budget relief for Carthage? Describe.
                </li>
                <li>
                    Will other gift or grant dollars be used to support
                    this project? Describe.
                </li>
                    What, if any financial commitments
                    (match/ cost-share/ in-kind will Carthage need to
                    make if awarded these funds?
                </li>
                <li>Does the grant allow for indirect costs? </li>
            </ul>
        """),
    )
    # additional comments
    comments = models.TextField(
        null=True,
        blank=True,
        help_text="Provide any additional comments if need be",
    )
    # administrative comments
    admin_comments = models.TextField(
        null=True,
        blank=True,
        help_text="""
            Provide any administrative comments that you might want
            others to consider.
        """,
    )

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['-created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal'

    def __unicode__(self):
        """Default data for display."""
        return "{0} ({1})".format(self.title, self.id)

    def get_absolute_url(self):
        """Returns the FQDN URL."""
        return 'https://{0}{1}'.format(
            settings.SERVER_URL,
            reverse('proposal_detail', args=(self.id,)),
        )

    def get_update_url(self):
        """Returns the URL for updating the proposal."""
        return 'https://{0}{1}'.format(
            settings.SERVER_URL,
            reverse('proposal_update', args=(self.id,)),
        )

    def get_slug(self):
        """Returns the proposal slug."""
        return 'proposal/'

    def permissions(self, user):
        """What can the user access in terms of viewing & approval process."""
        osp_group = settings.OSP_GROUP
        veep = User.objects.get(pk=settings.VEEP_TPOS)
        provost = User.objects.get(pk=settings.PROV_TPOS)

        perms = {
            'view': False,
            'approve': False,
            'decline': False,
            'close': False,
            'open': False,
            'needswork': False,
            'superuser': False,
            'approver': False,
            'level3': False,
            'level2': False,
            'level1': False,
        }

        # in_group includes an exception for superusers
        group = in_group(user, osp_group)

        chair_depts = chair_departments(user.id)

        # dean or chair?
        dc = chair_depts[1]

        # Dean?
        if dc == 'dean':
            perms['view'] = True
            perms['level3'] = True
            perms['open'] = True
            perms['needswork'] = True
            perms['decline'] = True
            perms['approve'] = 'level3'
        # VP for Business?
        elif user.id == veep.id:
            perms['view'] = True
            perms['level2'] = True
            perms['needswork'] = True
            perms['decline'] = True
            perms['approve'] = 'level2'
        # Provost?
        elif user.id == provost.id:
            perms['view'] = True
            perms['level1'] = True
            perms['needswork'] = True
            perms['decline'] = True
            perms['approve'] = 'level1'
            # provost might be an adhoc approver
            for approver in self.approvers.all():
                if approver.user == user:
                    perms['approver'] = True
        # Superuser?
        elif group:
            perms['view'] = True
            perms['open'] = True
            perms['close'] = True
            perms['superuser'] = True
            perms['needswork'] = True
            perms['decline'] = True
            perms['approve'] = 'superuser'
        elif self.user == user:
            perms['view'] = True
            perms['open'] = True
        # Ad-hoc approver?
        else:
            for approver in self.approvers.all():
                if approver.user == user:
                    perms['view'] = True
                    perms['approver'] = True
                    perms['needswork'] = True
                    perms['decline'] = True
                    perms['approve'] = 'approver'
                    break

        return perms

    # at the moment, we assume all approvers will be responsible for
    # step 1 AND step 2. in the future, i suspect that this might change.
    def step1(self):
        """Check if step 1 has been approved."""
        # Dean or Department VP
        approved = self.level3
        for approver in self.approvers.all():
            if not approver.step1:
                approved = False
                break
        return approved

    def step2(self):
        """Check if step 2 has been approved."""
        try:
            approved = (
                self.impact.level1 and
                self.impact.level2 and
                self.impact.level3
            )
        except AttributeError:
            approved = False

        if approved:
            for approver in self.approvers.all():
                if not approver.step2:
                    approved = False
                    break
        return approved

    def ready_level1(self):
        """Check if VP for Business (level2) & Provost (level1) can approve."""
        approved = False
        try:
            if self.impact.level3:
                approved = True
        except AttributeError:
            approved = False

        if approved:
            for approver in self.approvers.all():
                if not approver.step2:
                    approved = False
                    break

        return approved


class ProposalImpact(models.Model):
    """Proposal impact data."""

    # meta
    created_at = models.DateTimeField("Date Created", auto_now_add=True)
    updated_at = models.DateTimeField("Date Updated", auto_now=True)
    proposal = models.OneToOneField(
        Proposal,
        related_name='impact',
        on_delete=models.CASCADE,
    )
    # status
    level3 = models.BooleanField(default=False)  # Division Dean
    level2 = models.BooleanField(default=False)  # VP for Business
    level1 = models.BooleanField(default=False)  # Provost

    # institutional impacts
    institutional_funds = models.CharField(
        "Will institutional or departmental funds be used in this proposal?",
        max_length=4,
        choices=choices.BINARY_CHOICES,
    )
    institutional_funds_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    indirect_funds_solicitation = models.CharField(
        "Does the sponsor allow the inclusion of indirect in the budget?",
        max_length=4,
        choices=choices.BINARY_CHOICES,
    )
    indirect_funds_solicitation_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    subcontracts = models.ManyToManyField(
        GenericChoice,
        verbose_name="Does your proposal include any of the following?",
        limit_choices_to=limit_subcontracts,
        blank=True,
        related_name="subcontracts",
        help_text="Check all that apply",
    )
    subcontracts_details = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="""
            If you checked any of the boxes above, please provide additional
            details.
        """,
    )
    course_relief = models.CharField(
        """
            Will this project require that your department hire someone
            to teach the courses you are scheduled to teach
            or any other type of course relief?
        """,
        max_length=8,
        choices=choices.BINARY_CHOICES,
    )
    course_relief_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    new_hires = models.CharField(
        "Will this project create a new position at Carthage?",
        max_length=8,
        choices=choices.BINARY_CHOICES,
    )
    new_hires_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    infrastructure_requirements = models.CharField(
        "Is new or renovated space required?",
        max_length=8,
        choices=choices.UNSURE_CHOICES,
    )
    infrastructure_requirements_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    # begin questions after instructional text
    international = models.CharField(
        "International or off-campus studies",
        max_length=8,
        choices=choices.BINARY_CHOICES,
    )
    international_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    event_services = models.CharField(
        "Conferences and event services",
        max_length=8,
        choices=choices.BINARY_CHOICES,
    )
    event_services_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    financial_aid = models.CharField(
        "Financial aid / scholarships",
        max_length=8,
        choices=choices.BINARY_CHOICES,
    )
    financial_aid_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    students_involved = models.CharField(
        "Student Employment or Work Study",
        max_length=16,
        choices=choices.BINARY_CHOICES,
    )
    students_involved_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    students_stipends = models.CharField(
        "Student Stipends/ Scholarships/ Fellowships",
        max_length=16,
        choices=choices.BINARY_CHOICES,
    )
    students_stipends_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    personnel_salary = models.CharField(
        "Job posting, hiring, salary/wage changes",
        max_length=16,
        choices=choices.BINARY_CHOICES,
    )
    personnel_salary_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    data_management = models.CharField(
        "Institutional Data",
        max_length=8,
        choices=choices.BINARY_CHOICES,
    )
    data_management_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    tech_support = models.CharField(
        "Computer support, computer equipment, data management needs",
        max_length=8,
        choices=choices.BINARY_CHOICES,
    )
    tech_support_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    marketing = models.CharField(
        "Brochures, PR, websites",
        max_length=8,
        choices=choices.BINARY_CHOICES,
    )
    marketing_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    contract_procurement = models.CharField(
        "Contract Review and Negotiation",
        max_length=8,
        choices=choices.BINARY_CHOICES,
    )
    contract_procurement_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    purchase_equipment = models.CharField(
        "Equipment Purchases (over $5000)",
        max_length=8,
        choices=choices.BINARY_CHOICES,
    )
    purchase_equipment_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    subaward_monitoring = models.CharField(
        "Sub Award Monitoring",
        max_length=4,
        choices=choices.BINARY_CHOICES,
    )
    subaward_monitoring_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Please provide additional details",
    )
    human_subjects = models.CharField(
        "IRB (Human Subjects Research)",
        max_length=4,
        choices=choices.BINARY_CHOICES,
    )
    human_subjects_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Detail any IRB approval and submission date",
    )
    animal_subjects = models.CharField(
        "IACUC (Animal Research)",
        max_length=4,
        choices=choices.BINARY_CHOICES,
    )
    animal_subjects_detail = models.TextField(
        verbose_name="",
        null=True,
        blank=True,
        help_text="Detail any IACUC approval and submission dates",
    )
    admin_comments = models.TextField(
        null=True,
        blank=True,
        help_text="""
            Provide any administrative comments that you might want
            others to consider.
        """,
    )
    disclosure_assurance = models.BooleanField(default=False)

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['-created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal_impact'

    def title(self):
        """Obtain the proposal title from foreign key Proposal."""
        return self.proposal.title

    def get_slug(self):
        """Build the URL slug."""
        return 'proposal-impact/'


class ProposalBudget(models.Model):
    """Proposal budget data."""

    # meta
    created_at = models.DateTimeField(
        'Date Created', auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        'Date Updated', auto_now=True,
    )
    proposal = models.OneToOneField(
        Proposal,
        editable=False,
        related_name='budget',
        on_delete=models.CASCADE,
    )
    # Costs and totals
    total = models.DecimalField(
        "Total Program Cost",
        decimal_places=2,
        max_digits=16,
        help_text="Provide the total amount budgeted for this project",
        null=True,
        blank=True,
    )
    total_funding = models.DecimalField(
        "Provide the total funds requested from this grantor",
        decimal_places=2,
        max_digits=16,
        help_text="Provide the total amount of the funding request",
        null=True,
        blank=True,
    )
    plan_b = models.TextField(
        "Briefly describe your plan for this project if not awarded this grant",
        help_text="~200 words",
    )
    # Files
    budget_final = models.FileField(
        "Final Budget for Review",
        upload_to=upload_to_path,
        validators=FILE_VALIDATORS,
        max_length=512,
        help_text="PDF or Excel Format Only",
    )
    budget_justification_final = models.FileField(
        "Final Budget Justification for Review",
        upload_to=upload_to_path,
        validators=FILE_VALIDATORS,
        max_length=512,
        help_text="PDF or Excel Format Only",
        null=True,
        blank=True,
    )

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['-created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal_budget'

    def get_slug(self):
        """Build the URL slug."""
        return 'proposal-budget/'

    def __unicode__(self):
        """Build the default value."""
        return "{0}".format(self.proposal.title)


class ProposalBudgetFunding(models.Model):
    """Proposal budget funding data."""

    # meta
    created_at = models.DateTimeField(
        'Date Created', auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        'Date Updated', auto_now=True,
    )
    budget = models.ForeignKey(
        ProposalBudget,
        editable=False,
        related_name='funding',
        on_delete=models.CASCADE,
    )
    amount = models.DecimalField(
        "Amount/Currency",
        decimal_places=2,
        max_digits=16,
        null=True,
        blank=True,
    )
    source = models.CharField(
        "Describe Other Sources of Funding for the Project",
        max_length=24,
        choices=choices.BUDGET_FUNDING_SOURCE,
    )
    status = models.CharField(
        "Status of these Funds",
        max_length=24,
        choices=choices.BUDGET_FUNDING_STATUS,
    )

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal_budget_funding'

    def get_slug(self):
        """Build the URL slug."""
        return 'proposal-budget-funding/'

    def __unicode__(self):
        """Build the default value."""
        return "{0}".format(self.budget.proposal.title)


class ProposalDocument(models.Model):
    """Proposal supporting documents."""

    # meta
    created_at = models.DateTimeField(
        "Date Created",
        auto_now_add=True,
    )
    proposal = models.ForeignKey(
        Proposal,
        editable=False,
        related_name='documents',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        "Name or short description of the file",
        max_length=128,
        null=True,
        blank=True,
    )
    phile = models.FileField(
        "Supporting Document",
        upload_to=upload_to_path,
        validators=FILE_VALIDATORS,
        max_length=512,
        help_text="PDF or Excel Format Only",
        null=True,
        blank=True,
    )
    tags = TaggableManager(blank=True)

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['-created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal_document'

    def get_slug(self):
        """Build the URL slug."""
        return 'proposal-document/'

    def __unicode__(self):
        """Build the default value."""
        return "{0}: {1}".format(self.name, self.proposal.title)


class ProposalContact(models.Model):
    """Proposal contact data."""

    created_at = models.DateTimeField(
        "Date Created",
        auto_now_add=True,
    )
    proposal = models.ForeignKey(
        Proposal,
        editable=False,
        related_name='contact',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )
    institution = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )
    email = models.EmailField(
        "Your email address",
        max_length=128,
        null=True,
        blank=True,
    )
    tags = TaggableManager(blank=True)

    class Meta:
        """Attributes about the data model and admin options."""

        ordering = ['created_at']
        get_latest_by = 'created_at'
        db_table = 'core_proposal_contact'

    def get_slug(self):
        """Build the URL slug."""
        return 'proposal-contact/'

    def __unicode__(self):
        """Build the default value."""
        return "{0}: {1}".format(self.name, self.institution)


class ProposalApprover(models.Model):
    """Additional folks who need to approve a proposal."""

    user = models.ForeignKey(
        User,
        related_name='approver_user',
        on_delete=models.CASCADE,
    )
    proposal = models.ForeignKey(
        Proposal,
        related_name='approvers',
        on_delete=models.CASCADE,
    )
    # this field is not in use at the moment but i suspect
    # OSP will want to reactivate it in the future
    steps = models.CharField(
        max_length=4,
        default='3',
        choices=choices.PROPOSAL_STEPS_CHOICES,
    )
    replace = models.CharField(
        max_length=24,
        default='level3',
        choices=choices.APPROVAL_LEVEL_CHOICES,
        null=True,
        blank=True,
    )
    step1 = models.BooleanField(default=True)
    step2 = models.BooleanField(default=True)

    class Meta:
        """Attributes about the data model and admin options."""

        db_table = 'core_proposal_approver'

    def first_name(self):
        """Return the approver's first name."""
        return self.user.first_name

    def last_name(self):
        """Return the approver's last name."""
        return self.user.last_name

    def email(self):
        """Return the approver's email."""
        return self.user.email

    def title(self):
        """Return the proposal title."""
        return self.proposal.title
