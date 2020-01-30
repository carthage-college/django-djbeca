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

    institutional_funds = forms.TypedChoiceField(
        label="""
            Will institutional or departmental funds be used in this proposal?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    indirect_funds_solicitation = forms.TypedChoiceField(
        label="Does the sponsor allow the inclusion of indirect in the budget?",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    subaward_monitoring = forms.TypedChoiceField(
        label="Sub Award Monitoring",
        choices=choices.BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    human_subjects = forms.TypedChoiceField(
        label="IRB (Human Subjects Research)",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    animal_subjects = forms.TypedChoiceField(
        label="IACUC (Animal Research)",
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    students_involved = forms.TypedChoiceField(
        label="Student Employment or Work Study",
        choices=choices.BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    students_stipends = forms.TypedChoiceField(
        label="Student stipends",
        choices=choices.BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    personnel_salary = forms.TypedChoiceField(
        label="Job posting, hiring, salary/wage changes",
        choices=choices.BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    marketing = forms.TypedChoiceField(
        label="Brochures, PR, websites",
        choices=choices.BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    contract_procurement = forms.TypedChoiceField(
        label="Contract Review and Negotiation",
        choices=choices.BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    data_management = forms.TypedChoiceField(
        label="Institutional Data",
        choices=choices.BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    new_hires = forms.TypedChoiceField(
        label="Will this project create a new position at Carthage?",
        choices=choices.BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    course_relief = forms.TypedChoiceField(
        label="""
            Will this project require that your department hire someone
            to teach the courses you are scheduled to teach
            or any other type of course relief?
        """,
        choices=BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    infrastructure_requirements = forms.TypedChoiceField(
        label="Is new or renovated space required?",
        choices=choices.BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    international = forms.TypedChoiceField(
        label="International or off-campus studies",
        choices=choices.BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    event_services = forms.TypedChoiceField(
        label="Conferences and event services",
        choices=choices.BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    financial_aid = forms.TypedChoiceField(
        label="Financial aid / scholarships",
        choices=choices.BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    tech_support = forms.TypedChoiceField(
        label="Computer support, computer equipment, data management needs",
        choices=choices.BINARY_CHOICES,
        widget=forms.RadioSelect(),
    )
    purchase_equipment = forms.TypedChoiceField(
        label="Equipment Purchases (over $5000)",
        choices=choices.BINARY_CHOICES,
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

        #for key, _input in cd.items():
        #for key in cd.keys():
        for key in list(cd.keys()):
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
