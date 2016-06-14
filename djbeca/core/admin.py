from django.contrib import admin

from djbeca.core.models import Proposal

class ProposalAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'title',)

    date_hierarchy = 'created_at'
    ordering = [
        'user__last_name','user__first_name'
    ]
    search_fields = (
        'user__last_name','user__first_name','user__email','user__username'
    )
    list_per_page = 500
    raw_id_fields = ("user","updated_by")

    def first_name(self, obj):
        return obj.user.first_name

    def last_name(self, obj):
        return obj.user.last_name


admin.site.register(Proposal, ProposalAdmin)
