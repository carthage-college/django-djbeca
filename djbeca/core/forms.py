# -*- coding: utf-8 -*-

from django import forms

from djbeca.core.models import Proposal

class ProposalForm(forms.ModelForm):

    class Meta:
        model = Proposal
        #fields = '__all__'
        exclude = ('user',)
