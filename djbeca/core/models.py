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


class Proposal(models.Model):
    """
    Proposal to pursue funding
    """
    # meta
    created_at = models.DateTimeField(
        "Date Created", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        "Date Updated", auto_now=True
    )
    user = models.ForeignKey(User, editable=False)
    department_approved = models.BooleanField(default=False)
    division_approved = models.BooleanField(default=False)
    provost_approved = models.BooleanField(default=False)
    status = models.BooleanField(
        "Approved",
        default=False
    )
    # overview
    department = models.CharField(
        max_length=12
    )
    phone = models.CharField(
        verbose_name='Phone',
        max_length=12,
        help_text="Format: XXX-XXX-XXXX"
    )
    co_investigators = models.TextField(
        help_text = """
            Others who are responsible for the scientific or technical
            direction of the project (include department or affilication
            if not Carthage).
        """,
        null=True,blank=True
    )
    partner_lead = models.CharField(
        "Is Carthage the lead institution?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
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
    title = models.CharField(
        "Project title", max_length=255
    )
    start_date = models.DateField("Project start date")
    end_date = models.DateField("Project end date")
    grant_agency_program_name = models.CharField(
        verbose_name="Grant Agency and Program Name",
        max_length=128,
    )
    grant_agency_program_url = models.CharField(
        verbose_name="Grant Agency and Program Solicitation URL",
        max_length=768,
        null=True,blank=True,
        help_text="If available."
    )
    project_type = models.CharField(
        max_length=128,
        choices=PROJECT_TYPE_CHOICES,
    )
    summary = models.TextField(
        "Program summary (~1000 characters)",
        help_text="""
            Provide a brief description of your proposed project
            and how the proposed project addresses one or more
            strategies/goals in Carthage’s strategic plan.
        """
    )
    budget = models.FileField(
        upload_to=upload_to_path,
        #validators=[MimetypeValidator('application/pdf')],
        max_length=768,
        help_text="PDF format"
    )
    # Institutional Impact
    course_release = models.CharField(
        "Require course release or overload?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    course_release_details = models.TextField(
        "If so, please provide details",
        null=True,blank=True
    )
    grant_submission_requirement = models.CharField(
        """
            Satisfy the grant submission requirement for time/effort
            for each Carthage individual involved?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    partner_participation = models.CharField(
        """
            Partner Institution will devote the following percent
            of the total academic year effort to the project
        """,
        max_length=2,
        null=True,blank=True
    )
    sponsor_participation = models.CharField(
        """
            Sponsor will be charged the following percent of the
            above Partner Institution's effort
        """,
        max_length=2,
        null=True,blank=True
    )
    new_personnel = models.CharField(
        "Require new hires other than students?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    new_personnel_details = models.TextField(
        "If so, please provide details",
        null=True,blank=True
    )
    major_equipment = models.CharField(
        """
            Result in the purchase of major equipment?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    major_equipment_details = models.TextField(
        "If so, please provide details",
        null=True,blank=True
    )
    additional_space = models.CharField(
        """
            Require additional office, lab or other facilities or
            room modifications?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    additional_space_details = models.TextField(
        "If so, please provide details",
        null=True,blank=True
    )
    technology_support = models.CharField(
        """
            Involve technology use that will require extensive
            support from Technology Services?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    technology_support_details = models.TextField(
        "If so, please provide details",
        null=True,blank=True
    )
    # Compliance Requirements
    students = models.CharField(
        "Invole the use of students?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    patent_confidential = models.CharField(
        """
            Involve work that may result in a patent or involve
            proprietary or confidential information?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    human_subjects = models.CharField(
        "Use human subjects?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    human_review_submitted_date = models.DateField(
        "Date Human Subjects Review Form Submitted",
        null=True,blank=True
    )
    human_review_approved_date = models.DateField(
        "Date Human Subjects Review Form Approved",
        null=True,blank=True
    )
    other_participants = models.CharField(
        """
            Involve participation and/or subcontrators with other
            institutions/organizations?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    other_participants_details = models.TextField(
        "If so, please list",
        null=True,blank=True
    )
    hazzards = models.CharField(
        """
            Involve the use of chemical/physical hazards (including toxic or
            hazardous chemicals, radioactive material, biohazards, pathogens,
            toxins, recombinant DNA, oncogenic viruses, tumor cells, etc.)?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    international_collaboration = models.CharField(
        """
            Involve international travel, collaboration, export,
            international student participation?
        """,
        max_length=4,
        choices=BINARY_CHOICES,
    )
    animal_subjects = models.CharField(
        "Use animal subjects?",
        max_length=4,
        choices=BINARY_CHOICES,
    )
    animal_protocol_submitted_date = models.DateField(
        "Date IACUC Protocol Submitted",
        null=True,blank=True
    )
    animal_protocol_approved_date = models.DateField(
        "Date IACUC Protocol Approved",
        null=True,blank=True
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
            #reverse('admin:core_proposal_change',args=(self.id,))
            reverse('proposal_update',args=(self.id,))
        )

    def get_slug(self):
        return 'proposal/'
