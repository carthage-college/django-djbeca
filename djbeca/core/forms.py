# -*- coding: utf-8 -*-

from django import forms

from djbeca.core.models import Proposal

class ProposalForm(forms.ModelForm):

    def __init__(self, department_choices, *args, **kwargs):
        super(ProposalForm, self).__init__(*args, **kwargs)
        choices = ()
        if department_choices:
            choices = department_choices
        #self.fields['department'].choices = choices
        self.fields['department'].choices = department_choices

    department = forms.ChoiceField(
        label="Department",
        choices=()
    )

    class Meta:
        model = Proposal
        #fields = '__all__'
        exclude = ('user','funding','department_approved','division_approved')
