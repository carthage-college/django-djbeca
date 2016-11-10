# -*- coding: utf-8 -*-

from django import forms

from djbeca.core.models import FundingIdentified, FundingPursued
from djbeca.core.models import Proposal

from djbeca.core.choices import *

from djtools.fields import BINARY_CHOICES


class FundingIdentifiedForm(forms.ModelForm):
    classification = forms.TypedChoiceField(
        label="This proposal will classify Carthage as a",
        choices=CLASSIFICATION_CHOICES, widget=forms.RadioSelect(),
    )
    partner = forms.TypedChoiceField(
        label="Does this proposal partner with another institution?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect(),
    )
    sponsor_time_frame = forms.TypedChoiceField(
        label="Please choose the time frame",
        choices=TIME_FRAME_CHOICES, widget=forms.RadioSelect(),
    )
    amount_required = forms.DecimalField(
        widget=forms.TextInput(attrs={'placeholder': '$'}),
        help_text="In dollars"
    )
    support_facstaff = forms.TypedChoiceField(
        label="Will funds support faculty/staff devoted to project?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect(),
    )
    match_required = forms.TypedChoiceField(
        label="Cost Match Requirement",
        choices=BINARY_CHOICES, widget=forms.RadioSelect(),
    )
    undergraduates = forms.TypedChoiceField(
        label="Will funds support undergraduates?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect(),
    )
    room_board = forms.TypedChoiceField(
        label="Will Carthage room and board be needed?",
        choices=BINARY_CHOICES, widget=forms.RadioSelect(),
    )

    class Meta:
        model = FundingIdentified
        exclude = (
            'proposal',
        )


class FundingPursuedForm(forms.ModelForm):
    project_end = forms.TypedChoiceField(
        label="At the end of the project, it will",
        choices=PROJECT_END_CHOICES, widget=forms.RadioSelect()
    )
    amount_required = forms.DecimalField(
        widget=forms.TextInput(attrs={'placeholder': '$'}),
        help_text="In dollars"
    )

    class Meta:
        model = FundingPursued
        exclude = (
            'proposal',
        )

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

    class Meta:
        model = Proposal
        exclude = (
            'user','funding',
            'department_approved','division_approved','email_approved',
            'status'
        )


class ProposalUpdateForm(ProposalForm):

    funding_status = forms.TypedChoiceField(
        choices=FUNDING_CHOICES, widget=forms.RadioSelect()
    )

    class Meta:
        model = Proposal
        exclude = (
            'user',
            'department_approved','division_approved','email_approved',
            'status'
        )

