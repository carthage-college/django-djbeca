# -*- coding: utf-8 -*-

from django import forms

from djbeca.core.models import Proposal
from djbeca.core.choices import *

from djtools.fields import BINARY_CHOICES

from localflavor.us.forms import USPhoneNumberField


class ProposalForm(forms.ModelForm):

    def __init__(self, department_choices, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        choices = ()
        if department_choices:
            choices = department_choices
        self.fields['department'].choices = department_choices

    department = forms.ChoiceField(
        label="Department",
        choices=()
    )
    phone = USPhoneNumberField()
    partner_lead = forms.TypedChoiceField(
        label="Is Carthage the lead Institution?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    partner_institution = forms.CharField(
        label = "Name of Partner Institution(s)",
        required = False
    )
    partner_institution_contact = forms.CharField(
        label = "Partner Institution(s) contact information",
        help_text = "Sponsored Programs Office (or equivalent)",
        required = False,
        widget=forms.Textarea
    )
    start_date = forms.DateField(
        label = "Project start date",
    )
    end_date = forms.DateField(
        label = "Project end date",
    )
    # Institutional Impact
    course_release = forms.TypedChoiceField(
        label = "Require course release or overload?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect(),
    )
    grant_submission_requirement = forms.TypedChoiceField(
        label = """
            Satisfy the grant submission requirement for time/effort
            for each Carthage individual involved?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect(),
    )
    new_personnel = forms.TypedChoiceField(
        label = "Require new hires other than students?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect(),
    )
    major_equipment = forms.TypedChoiceField(
        label = "Result in the purchase of major equipment?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    additional_space = forms.TypedChoiceField(
        label = """
            Require additional office, lab or other facilities or
            room modifications?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    technology_support = forms.TypedChoiceField(
        label = """
            Involve technology use that will require extensive
            support from Technology Services?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    # Compliance Requirements
    students = forms.TypedChoiceField(
        label = "Invole the use of students?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    patent_confidential = forms.TypedChoiceField(
        label = """
            Involve work that may result in a patent or involve
            proprietary or confidential information?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    human_subjects = forms.TypedChoiceField(
        label = "Use human subjects?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    human_review_submitted_date = forms.DateField(
        label = "Date Human Subjects Review Form Submitted",
        required=False
    )
    human_review_approved_date = forms.DateField(
        label = "Date Human Subjects Review Form Approved",
        required=False
    )
    other_participants = forms.TypedChoiceField(
        label = """
            Involve participation and/or subcontrators with other
            institutions/organizations?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    hazzards = forms.TypedChoiceField(
        label = """
            Involve the use of chemical/physical hazards (including toxic or
            hazardous chemicals, radioactive material, biohazards, pathogens,
            toxins, recombinant DNA, oncogenic viruses, tumor cells, etc.)?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    international_collaboration = forms.TypedChoiceField(
        label = """
            Involve international travel, collaboration, export,
            international student participation?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    animal_subjects = forms.TypedChoiceField(
        label = "Use animal subjects?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    animal_protocol_submitted_date = forms.DateField(
        label = "Date IACUC Protocol Submitted",
        required=False
    )
    animal_protocol_approved_date = forms.DateField(
        label = "Date IACUC Protocol Approved",
        required=False
    )

    class Meta:
        model = Proposal
        exclude = (
            'user','created_at','updated_at',
            'department_approved','division_approved','provost_approved'
        )


class ProposalUpdateForm(forms.ModelForm):

    class Meta:
        model = Proposal
        exclude = (
            'user','created_at','updated_at','department',
            'department_approved','division_approved','provost_approved'
        )
