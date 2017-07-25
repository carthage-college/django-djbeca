# -*- coding: utf-8 -*-

from django import forms

from djbeca.core.models import Proposal
from djbeca.core.models import ProposalBudget, ProposalImpact
from djbeca.core.choices import *

from djtools.fields import BINARY_CHOICES
from djtools.fields.time import KungfuTimeField

from directory.core import FACSTAFF_ALPHA

from djzbar.utils.informix import do_sql

valid_time_formats = ['%P', '%H:%M%A', '%H:%M %A', '%H:%M%a', '%H:%M %a']


class ProposalForm(forms.ModelForm):

    def __init__(self, department_choices, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        choices = ()
        if department_choices:
            choices = department_choices
        self.fields['department'].choices = department_choices

    # Basic Proposal Elements
    grant_deadline_time = forms.TimeField(
        label="Proposal deadline time",
        #widget=TimeInput(format='%I:%H %p')
    )
    # Investigator Information
    # NOTE: we have name, email, ID from user profile data
    department = forms.ChoiceField(
        label="Department",
        choices=()
    )
    # NOTE: "Co-Principal Investigators & Associated Institution"
    # are GenericContact() Foreign Key relationships.
    # Name, Institution fields [limit 5]
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
    '''
    budget_total = forms.DecimalField(
        label="Total Budget Request",
        widget=forms.TextInput(attrs={'placeholder':"$"}),
        help_text="List the total amount budgeted for this project"
    )
    '''

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


class GoalsForm(forms.Form):
    name_1 = forms.TypedChoiceField(
        label="Goal Type",
        choices=PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False
    )
    description_1 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False
    )
    name_2 = forms.TypedChoiceField(
        label="Goal Type",
        choices=PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False
    )
    description_2 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False
    )
    name_3 = forms.TypedChoiceField(
        label="Goal Type",
        choices=PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False
    )
    description_3 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False
    )
    name_4 = forms.TypedChoiceField(
        label="Goal Type",
        choices=PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False
    )
    description_4 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False
    )
    name_5 = forms.TypedChoiceField(
        label="Goal Type",
        choices=PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False
    )
    description_5 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False
    )
    name_6 = forms.TypedChoiceField(
        label="Goal Type",
        choices=PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False
    )
    description_6 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False
    )
    name_7 = forms.TypedChoiceField(
        label="Goal Type",
        choices=PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False
    )
    description_7 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False
    )
    name_8 = forms.TypedChoiceField(
        label="Goal Type",
        choices=PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False
    )
    description_8 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False
    )


class BudgetForm(forms.ModelForm):

    class Meta:
        model = ProposalBudget
        exclude = (
            'proposal','created_at','updated_at',
            'level2_approved','level1_approved'
        )


class ImpactForm(forms.ModelForm):

    course_release = forms.TypedChoiceField(
        label = "Does this proposal require course release or overload?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )

    additional_pay = forms.TypedChoiceField(
        label = "Does this proposal require additional pay?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    payout_students = forms.TypedChoiceField(
        label = "Does this proposal require payout to Carthage students?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    new_positions = forms.TypedChoiceField(
        label = """
            Does this proposal require the creation of new Carthage positions?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    purchase_equipment = forms.TypedChoiceField(
        label = """
            Does this proposal result in the purchase of major equipment,
            costing over $5,000?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    infrastructure_modifications = forms.TypedChoiceField(
        label = """
            Does this proposal require additional office,
            lab or other facilities or room modifications?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    institutional_review = forms.TypedChoiceField(
        label = "Does this proposal require review of IRB and/or IACUC?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    institutional_review_date = forms.DateField(
        label = "If 'Yes', please provide the approval date",
        required=False
    )
    cost_share_match = forms.TypedChoiceField(
        label = "Does this proposal require cost share/match?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    voluntary_committment = forms.TypedChoiceField(
        label = "Does this proposal contain any voluntary commitment?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect(),
        help_text = "e.g. faculty/staff time, cost share/match"
    )

    class Meta:
        model = ProposalImpact
        exclude = (
            'proposal','created_at','updated_at',
            'level2_approved','level1_approved'
        )


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
        label="Forms",
        choices = PROPOSAL_STEPS_CHOICES
    )


class EmailInvestigatorForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea, label="Email content"
    )

