from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

from djzbar.utils.hr import department
from djbeca.core.models import Proposal

class ProposalAdmin(admin.ModelAdmin):
    list_display = (
        'last_name', 'first_name', 'title',
        'department_approved','division_approved','status','provost_approved'
    )
    date_hierarchy = 'created_at'
    ordering = [
        'user__last_name','user__first_name',
        'department_approved','division_approved','status','provost_approved'
    ]
    readonly_fields = (
        'user','title','department_name','summary_strip','provost_approved'
    )
    fields = (
        'user','department_name','title','summary_strip',
        'department_approved','division_approved','status','provost_approved'
    )
    search_fields = (
        'user__last_name','user__first_name','user__email','user__username'
    )
    list_per_page = 500
    raw_id_fields = ("user",)

    class Media:
        js = [
            '/static/djtinue/grappelli/tinymce/jscripts/tiny_mce/tiny_mce.js',
            '/static/djtinue/grappelli/tinymce_setup/tinymce_setup.js',
        ]

    def department_name(self, instance):
        return department(instance.department)[0]
    department_name.short_description = 'Department'

    def summary_strip(self, instance):
        return mark_safe(instance.summary)
    summary_strip.short_description = 'Summary'

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name

    def response_change(self, request, obj):
        '''
        Redirect to dashboard after update
        '''
        response = super(ProposalAdmin, self).response_change(request, obj)
        '''
        if (isinstance(response, HttpResponseRedirect) and
                response['location'] == '../'):
            response['location'] = obj.get_absolute_url()
        return response
        '''
        response['location'] = obj.get_absolute_url()
        return response

admin.site.register(Proposal, ProposalAdmin)
