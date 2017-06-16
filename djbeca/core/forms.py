# -*- coding: utf-8 -*-

from django import forms

from djbeca.core.models import Proposal, ProposalApprover
from djbeca.core.choices import *

from djtools.fields import BINARY_CHOICES
from djtools.fields.time import KungfuTimeField

from directory.core import FACSTAFF_ALPHA

from djzbar.utils.informix import do_sql

from localflavor.us.forms import USPhoneNumberField

valid_time_formats = ['%P', '%H:%M%A', '%H:%M %A', '%H:%M%a', '%H:%M %a']


class ProposalForm(forms.ModelForm):

    def __init__(self, department_choices, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        choices = ()
        if department_choices:
            choices = department_choices
        self.fields['department'].choices = department_choices

    # Basic Proposal Elements
    proposal_submission_entity = forms.TypedChoiceField(
        label = "Who is required to submit the final submission?",
        choices=PROPOSAL_SUBMISSION_ENTITY_CHOICES,
        widget=forms.RadioSelect()
    )
    proposal_submission_method = forms.TypedChoiceField(
        label = "How is the proposal to be submitted?",
        choices=PROPOSAL_SUBMISSION_METHOD_CHOICES,
        widget=forms.RadioSelect()
    )
    #grant_deadline_time = KungfuTimeField(
    #    label="Proposal deadline time"
    #)
    grant_deadline_time = forms.TimeField(
        label="Proposal deadline time",
        #widget=TimeInput(format='%I:%H %p')
    )
    # Investigator Information
    # NOTE: we have name, email, ID from user profile data
    phone = USPhoneNumberField()
    department = forms.ChoiceField(
        label="Department",
        choices=()
    )
    # NOTE: "Co-Principal Investigators & Associated Institution"
    # are GenericContact() Foreign Key relationships.
    # Name, Instituion fields [limit 5]
    partner_institutions = forms.TypedChoiceField(
        label = "Are other institutions involved?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect()
    )
    # NOTE: "List all institutions involved"
    # are GenericContact() FK relationships.
    # Name field [limit 5]
    lead_institution = forms.TypedChoiceField(
        label = "Is Carthage College the lead institution on this project?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
        required=False
    )
    # Project Overview
    start_date = forms.DateField(
        label = "Project start date",
    )
    end_date = forms.DateField(
        label = "Project end date",
    )

    # Project Funding/ Budget Overview
    time_frame = forms.TypedChoiceField(
        label = "Is this one year funding or multi-year?",
        choices=TIME_FRAME_CHOICES,
        widget=forms.RadioSelect()
    )

    class Meta:
        model = Proposal
        exclude = (
            'user','created_at','updated_at',
            'level2_approved','level1_approved'
        )


class InstitutionsForm(forms.Form):
    institution_1 = forms.CharField(required=False)
    institution_2 = forms.CharField(required=False)
    institution_3 = forms.CharField(required=False)
    institution_4 = forms.CharField(required=False)
    institution_5 = forms.CharField(required=False)


class InvestigatorsForm(forms.Form):
    name_1 = forms.CharField(required=False)
    name_2 = forms.CharField(required=False)
    name_3 = forms.CharField(required=False)
    name_4 = forms.CharField(required=False)
    name_5 = forms.CharField(required=False)
    institution_1 = forms.CharField(required=False)
    institution_2 = forms.CharField(required=False)
    institution_3 = forms.CharField(required=False)
    institution_4 = forms.CharField(required=False)
    institution_5 = forms.CharField(required=False)


    '''

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
    '''


class ProposalApproverForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ProposalApproverForm, self).__init__(*args, **kwargs)

        results = do_sql(FACSTAFF_ALPHA)
        facstaff = [('','-----------')]
        cid = None
        for r in results:
            if cid != r.id:
                name = '{}, {}'.format(r.lastname, r.firstname)
                facstaff.append((r.id, name))
                cid = r.id
        proposals = [('','-----------')]
        self.fields['user'].choices = facstaff

        for p in Proposal.objects.all():
            title = '{}: by {}, {}'.format(
                p.title, p.user.last_name, p.user.first_name
            )
            proposals.append((p.id,title))
        self.fields['proposal'].choices = proposals

    user = forms.ChoiceField(
        label="Faculty/Staff",
        choices=()
    )
    proposal = forms.ChoiceField(
        label="Proposal",
        choices=()
    )
    steps = forms.ChoiceField(
        label="Steps",
        choices = PROJECT_STEPS_CHOICES
    )


class EmailInvestigatorForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea, label="Email content"
    )

