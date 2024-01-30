# -*- coding: utf-8 -*-

"""Admin classes for data models."""

from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from djbeca.core.models import GenericChoice
from djbeca.core.models import Proposal
from djbeca.core.models import ProposalApprover
from djbeca.core.models import ProposalBudget
from djbeca.core.models import ProposalContact
from djbeca.core.models import ProposalDocument
from djbeca.core.models import ProposalImpact


class GenericChoiceAdmin(admin.ModelAdmin):
    """GenericChoice admin class."""

    list_display = ('name', 'value', 'rank', 'active', 'admin')
    list_editable = ('active', 'admin')
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


class ProposalAdmin(admin.ModelAdmin):
    """Proposal admin class."""

    list_display = (
        'last_name',
        'first_name',
        'title',
        'level3',
        'awarded',
        'created_at',
        'updated_at',
    )
    list_editable = ('awarded',)
    date_hierarchy = 'created_at'
    #readonly_fields = ('user',)
    ordering = (
        '-created_at', 'user__last_name', 'user__first_name', 'level3',
    )
    search_fields = (
        'user__last_name', 'user__first_name', 'user__email', 'user__username',
    )
    list_per_page = 500
    raw_id_fields = ('user',)

    class Media:
        """Static files like javascript and style sheets."""

        js = [
            '/static/djtinue/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
            '/static/djtinue/grappelli/tinymce_setup/tinymce_setup.js',
        ]

    def summary_strip(self, instance):
        """Mark html content for summary field as safe."""
        return mark_safe(instance.summary)
    summary_strip.short_description = 'Summary'

    def first_name(self, proposal):
        """Return the proposal author's first name."""
        return proposal.user.first_name

    def last_name(self, proposal):
        """Return the proposal author's last name."""
        return proposal.user.last_name


class ProposalContactAdmin(admin.ModelAdmin):
    """Proposal contacts admin class."""

    list_per_page = 500
    raw_id_fields = ('proposal',)
    date_hierarchy = 'created_at'
    list_display = ('name', 'email', 'institution', 'created_at', 'proposal')


class ProposalApproverAdmin(admin.ModelAdmin):
    """Proposal approver admin class."""

    list_per_page = 500
    raw_id_fields = ('proposal', 'user')
    list_display = ('title', 'last_name', 'first_name', 'email')


class ProposalBudgetAdmin(admin.ModelAdmin):
    """Proposal budget admin class."""

    list_per_page = 500
    raw_id_fields = ('proposal',)


class ProposalDocumentAdmin(admin.ModelAdmin):
    """Proposal documents admin class."""

    list_per_page = 500
    raw_id_fields = ('proposal',)


class ProposalImpactAdmin(admin.ModelAdmin):
    """Proposal impacts admin class."""

    list_per_page = 500
    raw_id_fields = ('proposal',)
    list_display = (
        'title',
        'created_at',
        'updated_at',
        'level3',
        'level2',
        'level1',
        'disclosure_assurance',
    )
    date_hierarchy = 'created_at'
    ordering = (
        '-created_at',
        'level3',
        'level2',
        'level1',
        'disclosure_assurance',
    )


admin.site.register(GenericChoice, GenericChoiceAdmin)
admin.site.register(Proposal, ProposalAdmin)
admin.site.register(ProposalApprover, ProposalApproverAdmin)
admin.site.register(ProposalBudget, ProposalBudgetAdmin)
admin.site.register(ProposalDocument, ProposalDocumentAdmin)
admin.site.register(ProposalContact, ProposalContactAdmin)
admin.site.register(ProposalImpact, ProposalImpactAdmin)
