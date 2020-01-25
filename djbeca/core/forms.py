# -*- coding: utf-8 -*-

from django import forms
from djbeca.core import choices
from djbeca.core.models import Proposal
from djbeca.core.models import ProposalBudget
from djbeca.core.models import ProposalDocument
from djbeca.core.models import ProposalImpact
from djbeca.core.utils import get_proposals
from djimix.people.utils import get_peeps
from djtools.fields import BINARY_CHOICES


class ProposalForm(forms.ModelForm):
    """Proposal form for the data model."""

    def __init__(self, department_choices, *args, **kwargs):
        """Set the department field choices."""
        super(ProposalForm, self).__init__(*args, **kwargs)
        self.fields['department'].choices = department_choices

    # Investigator Information
    # NOTE: we have name, email, ID from user profile data
    department = forms.ChoiceField(
        label='Department',
        choices=(),
    )
    # NOTE "Co-Principal Investigators & Associated Institution"
    # are GenericContact() Foreign Key relationships.
    # Name, Institution fields [limit 5]
    # NOTE "List all institutions involved"
    # are GenericContact() FK relationships.
    # Name field [limit 5]

    # Project Overview
    start_date = forms.DateField(
        label="Project start date",
    )
    end_date = forms.DateField(
        label="Project end date",
    )

    class Meta:
        """Attributes about the form class."""

        model = Proposal
        exclude = (
            'opened',
            'closed',
            'user',
            'created_at',
            'updated_at',
            'email_approved',
            'save_submit',
            'decline',
            'level3',
            'comments',
        )

    def clean_project_type_other(self):
        """Insure that other value is populated."""
        cd = self.cleaned_data
        other = cd.get('project_type_other')
        if cd.get('project_type') == 'Other' and not other:
            self.add_error(
                'project_type_other',
                "Please provide additional information about the project type",
            )

        return other


class InstitutionsForm(forms.Form):
    """Institutions form."""

    institution1 = forms.CharField(required=False)
    institution2 = forms.CharField(required=False)
    institution3 = forms.CharField(required=False)
    institution4 = forms.CharField(required=False)
    institution5 = forms.CharField(required=False)


class InvestigatorsForm(forms.Form):
    """Ivestigators form."""

    name1 = forms.CharField(required=False)
    name2 = forms.CharField(required=False)
    name3 = forms.CharField(required=False)
    name4 = forms.CharField(required=False)
    name5 = forms.CharField(required=False)
    institution1 = forms.CharField(required=False)
    institution2 = forms.CharField(required=False)
    institution3 = forms.CharField(required=False)
    institution4 = forms.CharField(required=False)
    institution5 = forms.CharField(required=False)


class GoalsForm(forms.Form):
    """Goals form."""

    name1 = forms.TypedChoiceField(
        label="Goal Type",
        choices=choices.PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False,
    )
    description1 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False,
    )
    name2 = forms.TypedChoiceField(
        label="Goal Type",
        choices=choices.PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False,
    )
    description2 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False,
    )
    name3 = forms.TypedChoiceField(
        label="Goal Type",
        choices=choices.PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False,
    )
    description3 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False,
    )
    name4 = forms.TypedChoiceField(
        label="Goal Type",
        choices=choices.PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False,
    )
    description4 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False,
    )
    name5 = forms.TypedChoiceField(
        label="Goal Type",
        choices=choices.PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False,
    )
    description5 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False,
    )
    name6 = forms.TypedChoiceField(
        label="Goal Type",
        choices=choices.PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False,
    )
    description6 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False,
    )
    name7 = forms.TypedChoiceField(
        label="Goal Type",
        choices=choices.PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False,
    )
    description7 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False,
    )
    name8 = forms.TypedChoiceField(
        label="Goal Type",
        choices=choices.PROPOSAL_GOAL_CHOICES,
        widget=forms.Select(),
        required=False,
    )
    description8 = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        required=False,
    )


class BudgetForm(forms.ModelForm):
    """Proposal Budget form."""

    class Meta:
        """Attributes about the form class."""

        model = ProposalBudget
        exclude = (
            'proposal', 'created_at', 'updated_at',
        )


class ImpactForm(forms.ModelForm):
    """Proposal impact form."""

    cost_share_match = forms.TypedChoiceField(
        label="Does this proposal require cost sharing/match?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    funds = forms.TypedChoiceField(
        label="The budget requires:",
        choices=choices.FUNDS_CHOICES,
        widget=forms.RadioSelect(),
    )
    indirect_funds_solicitation = forms.TypedChoiceField(
        label="""
            Does the sponsor disallow the use of indirect funds
            per sponsor policy and/or solicitation?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    human_subjects = forms.TypedChoiceField(
        label="Does this proposal involve human subjects?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    animal_subjects = forms.TypedChoiceField(
        label="Does this proposal involve the use/care of animals?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    additional_work_load = forms.TypedChoiceField(
        label="""
            Will your work in this proposal be "in addition" to your current
            load and/or institutional obligations?
        """,
        choices=choices.UNSURE_CHOICES,
        widget=forms.RadioSelect(),
    )
    students_involved = forms.TypedChoiceField(
        label="""
            Does this proposal require support for students in the following?
        """,
        choices=choices.STUDENTS_INVOLVED_CHOICES,
        widget=forms.RadioSelect(),
    )
    contract_procurement = forms.TypedChoiceField(
        label="Does this proposal require contract (procurement) services?",
        choices=choices.UNSURE_CHOICES,
        widget=forms.RadioSelect(),
    )
    data_management = forms.TypedChoiceField(
        label="Does this proposal a data management plan?",
        choices=choices.UNSURE_CHOICES,
        widget=forms.RadioSelect(),
    )
    voluntary_committment = forms.TypedChoiceField(
        label="""
        Does this proposal contain any voluntary commitments
        on behalf of the College?
        """,
        choices=choices.BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    subcontractors_subawards = forms.TypedChoiceField(
        label="""
        Does this proposal involve subcontracts and/or subawards
        with other institutions/organizations?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    new_hires = forms.TypedChoiceField(
        label="Does this proposal require any new faculty or staff hires?",
        choices=choices.UNSURE_CHOICES,
        widget=forms.RadioSelect(),
    )
    course_relief = forms.TypedChoiceField(
        label="""
        Does this proposal contain course relief of any Carthage personnel
        during the academic year?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    service_overload = forms.TypedChoiceField(
        label="""
        Does this proposal contain extra service or overload
        of any Carthage personnnel?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    irb_review = forms.TypedChoiceField(
        label="Does this proposal require review of IRB?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    iacuc_review = forms.TypedChoiceField(
        label="Does this proposal require review of IACUC?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    international = forms.TypedChoiceField(
        label="""
        Does this proposal involve international travel, collaboration,
        export, international student participation?
        """,
        choices=choices.UNSURE_CHOICES,
        widget=forms.RadioSelect(),
    )
    hazards = forms.TypedChoiceField(
        label="""
        Does this proposal involve the use of chemical/physical hazards
        (including toxic or hazardous chemicals, radioactive material,
        biohazards, pathogens, toxins, recombinant DNA, oncongenic viruses,
        tumor cells, etc.)?
        """,
        choices=choices.UNSURE_CHOICES,
        widget=forms.RadioSelect(),
    )
    proprietary_confidential = forms.TypedChoiceField(
        label="""
        Does this proposal involve work that may result in a patent
        or involve proprietary or confidential information?
        """,
        choices=choices.UNSURE_CHOICES,
        widget=forms.RadioSelect(),
    )
    tech_support = forms.TypedChoiceField(
        label="""
        Does this proposal involve technology use that will require
        extensive technical support?
        """,
        choices=choices.UNSURE_CHOICES,
        widget=forms.RadioSelect(),
    )
    purchase_equipment = forms.TypedChoiceField(
        label="""
        Does this proposal require any purchase, installation,
        and maintenance of equipment?
        """,
        choices=choices.UNSURE_CHOICES,
        widget=forms.RadioSelect(),
    )
    infrastructure_requirements = forms.TypedChoiceField(
        label="""
        Does this proposal require any additional space than
        currently provided?
        """,
        choices=choices.UNSURE_CHOICES,
        widget=forms.RadioSelect(),
    )
    admin_comments = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="""
            Provide any administrative comments that you might want
            others to consider.
        """,
    )
    disclosure_assurance = forms.BooleanField(required=True)

    class Meta:
        """Attributes about the form class."""

        model = ProposalImpact
        exclude = (
            'proposal',
            'created_at',
            'updated_at',
            'level3',
            'level2',
            'level1',
        )

    def clean(self):
        """Form validation for various fields."""
        cd = self.cleaned_data

        for key, _input in cd.items():
            if '_detail' in key:
                radio = cd.get(key.split('_detail')[0])
                error = (
                    radio
                    and (radio == 'Yes' or 'Student' in radio)
                    and not cd.get(key)
                )
                if error:
                    self.add_error(key, "Please provide additional information")

        return cd


class DocumentForm(forms.ModelForm):
    """Proposal documents form."""

    def __init__(self, *args, **kwargs):
        """Add placeholder value to fields."""
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Name or short description'

    class Meta:
        """Attributes about the form class."""

        model = ProposalDocument
        fields = ('name', 'phile')


class CommentsForm(forms.Form):
    """Proposal comments form."""

    comments = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text="Provide any additional comments if need be",
    )


class ProposalApproverForm(forms.Form):
    """Proposal approver form."""

    def __init__(self, *args, **kwargs):
        """Set up choices for select field."""
        user = kwargs.pop('user')
        super(ProposalApproverForm, self).__init__(*args, **kwargs)

        # populate the approvers select field with faculty/staff
        facstaff = get_peeps('facstaff')
        approvers = [('', '-----------')]
        cid = None
        for fac in facstaff:
            if cid != fac['cid']:
                name = '{0}, {1}'.format(fac['lastname'], fac['firstname'])
                approvers.append((fac['cid'], name))
                cid = fac['cid']
        self.fields['user'].choices = approvers

        # populate the proposals select field
        proposals = get_proposals(user)
        if proposals['objects']:
            props = [('', '-----------')]
            for prop in proposals['objects']:
                title = '{0}: by {1}, {2}'.format(
                    prop.title, prop.user.last_name, prop.user.first_name,
                )
                props.append((prop.id, title))
            self.fields['proposal'].choices = props
        else:
            self.fields['proposal'].widget.attrs['class'] = 'error'

    user = forms.ChoiceField(label="Faculty/Staff", choices=())
    proposal = forms.ChoiceField(label="Proposal", choices=())


class EmailInvestigatorForm(forms.Form):
    """Send an email to investigator form."""

    content = forms.CharField(widget=forms.Textarea, label="Email content")
