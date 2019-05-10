# -*- coding: utf-8 -*-

from django import forms

from djbeca.core.models import Proposal
from djbeca.core.models import ProposalBudget, ProposalDocument, ProposalImpact
from djbeca.core.choices import *
from djbeca.core.utils import get_proposals

from djtools.fields import BINARY_CHOICES

from djzbar.core.sql import FACSTAFF_ALPHA
from djzbar.utils.informix import do_sql


class ProposalForm(forms.ModelForm):

    def __init__(self, department_choices, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        choices = ()
        if department_choices:
            choices = department_choices
        self.fields['department'].choices = department_choices

    # Investigator Information
    # NOTE: we have name, email, ID from user profile data
    department = forms.ChoiceField(
        label="Department",
        choices=()
    )
    # NOTE: "Co-Principal Investigators & Associated Institution"
    # are GenericContact() Foreign Key relationships.
    # Name, Institution fields [limit 5]
    # NOTE: "List all institutions involved"
    # are GenericContact() FK relationships.
    # Name field [limit 5]

    # Project Overview
    start_date = forms.DateField(
        label = "Project start date",
    )
    end_date = forms.DateField(
        label = "Project end date",
    )

    # Project Funding/ Budget Overview
    '''
    time_frame = forms.TypedChoiceField(
        label = "Is this one year funding or multi-year?",
        choices=TIME_FRAME_CHOICES,
        widget=forms.RadioSelect()
    )
    '''

    class Meta:
        model = Proposal
        exclude = (
            'opened','closed','user','created_at','updated_at',
            'email_approved','save_submit','decline','level3','comments'
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
        )


class ImpactForm(forms.ModelForm):

    cost_share_match = forms.TypedChoiceField(
        label = "Does this proposal require cost sharing/match?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    funds = forms.TypedChoiceField(
        label = "The budget requires:",
        choices=FUNDS_CHOICES, widget=forms.RadioSelect()
    )
    indirect_funds_solicitation = forms.TypedChoiceField(
        label = """
            Does the sponsor disallow the use of indirect funds
            per sponsor policy and/or solicitation?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    human_subjects = forms.TypedChoiceField(
        label = "Does this proposal involve human subjects?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    animal_subjects = forms.TypedChoiceField(
        label = "Does this proposal involve the use/care of animals?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    additional_work_load = forms.TypedChoiceField(
        label = """
            Will your work in this proposal be "in addition" to your current
            load and/or institutional obligations?
        """,
        choices=BINARY_UNSURE_CHOICES, widget=forms.RadioSelect()
    )
    students_involved = forms.TypedChoiceField(
        label = """
            Does this proposal require support for students in the following?
        """,
        choices=STUDENTS_INVOLVED_CHOICES, widget=forms.RadioSelect()
    )
    contract_procurement = forms.TypedChoiceField(
        label = "Does this proposal require contract (procurement) services?",
        choices=BINARY_UNSURE_CHOICES, widget=forms.RadioSelect()
    )
    data_management = forms.TypedChoiceField(
        label = "Does this proposal a data management plan?",
        choices=BINARY_UNSURE_CHOICES, widget=forms.RadioSelect()
    )
    voluntary_committment = forms.TypedChoiceField(
        label = """
        Does this proposal contain any voluntary commitments
        on behalf of the College?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    subcontractors_subawards = forms.TypedChoiceField(
        label = """
        Does this proposal involve subcontracts and/or subawards
        with other institutions/organizations?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    new_hires = forms.TypedChoiceField(
        label = "Does this proposal require any new faculty or staff hires?",
        choices=BINARY_UNSURE_CHOICES, widget=forms.RadioSelect()
    )
    course_relief = forms.TypedChoiceField(
        label = """
        Does this proposal contain course relief of any Carthage personnel
        during the academic year?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    service_overload = forms.TypedChoiceField(
        label = """
        Does this proposal contain extra service or overload
        of any Carthage personnnel?
        """,
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    irb_review = forms.TypedChoiceField(
        label = "Does this proposal require review of IRB?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    iacuc_review = forms.TypedChoiceField(
        label = "Does this proposal require review of IACUC?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect()
    )
    international = forms.TypedChoiceField(
        label = """
        Does this proposal involve international travel, collaboration,
        export, international student participation?
        """,
        choices=BINARY_UNSURE_CHOICES, widget=forms.RadioSelect()
    )
    hazards = forms.TypedChoiceField(
        label = """
        Does this proposal involve the use of chemical/physical hazards
        (including toxic or hazardous chemicals, radioactive material,
        biohazards, pathogens, toxins, recombinant DNA, oncongenic viruses,
        tumor cells, etc.)?
        """,
        choices=BINARY_UNSURE_CHOICES, widget=forms.RadioSelect()
    )
    proprietary_confidential = forms.TypedChoiceField(
        label = """
        Does this proposal involve work that may result in a patent
        or involve proprietary or confidential information?
        """,
        choices=BINARY_UNSURE_CHOICES, widget=forms.RadioSelect()
    )
    tech_support = forms.TypedChoiceField(
        label = """
        Does this proposal involve technology use that will require
        extensive technical support?
        """,
        choices=BINARY_UNSURE_CHOICES, widget=forms.RadioSelect()
    )
    purchase_equipment = forms.TypedChoiceField(
        label = """
        Does this proposal require any purchase, installation,
        and maintenance of equipment?
        """,
        choices=BINARY_UNSURE_CHOICES, widget=forms.RadioSelect()
    )
    infrastructure_requirements = forms.TypedChoiceField(
        label = """
        Does this proposal require any additional space than
        currently provided?
        """,
        choices=BINARY_UNSURE_CHOICES, widget=forms.RadioSelect()
    )
    admin_comments = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="""
            Provide any administrative comments that you might want
            others to consider.
        """
    )
    disclosure_assurance = forms.BooleanField(required = True)

    class Meta:
        model = ProposalImpact
        exclude = (
            'proposal','created_at','updated_at',
            'level3','level2','level1'
        )

    def clean(self):
        cd = self.cleaned_data

        for key, val in cd.items():
            if '_detail' in key:
                radio = cd.get(key.split('_detail')[0])
                if radio and (radio == 'Yes' or 'Student' in radio) and not cd.get(key):
                    self.add_error(key,"Please provide additional information")

        return cd


class DocumentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = \
          'Name or short description'

    class Meta:
        model = ProposalDocument
        fields = ('name','phile',)


class CommentsForm(forms.Form):
    comments = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Provide any additional comments if need be"
    )


class ProposalApproverForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ProposalApproverForm, self).__init__(*args, **kwargs)

        # populate the approvers select field with faculty/staff
        facstaff = do_sql(FACSTAFF_ALPHA)
        approvers = [('','-----------')]
        cid = None
        for r in facstaff:
            if cid != r.id:
                name = u'{}, {}'.format(r.lastname, r.firstname)
                approvers.append((r.id, name))
                cid = r.id
        self.fields['user'].choices = approvers

        # populate the proposals select field
        proposals = get_proposals(user)
        if proposals['objects']:
            props = [('','-----------')]
            for p in proposals['objects']:
                title = u'{}: by {}, {}'.format(
                    p.title, p.user.last_name, p.user.first_name
                )
                props.append((p.id,title))
            self.fields['proposal'].choices = props
        else:
            self.fields['proposal'].widget.attrs['class'] = 'error'

    user = forms.ChoiceField(
        label="Faculty/Staff",
        choices=()
    )
    proposal = forms.ChoiceField(
        label="Proposal",
        choices=()
    )


class EmailInvestigatorForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea, label="Email content"
    )

