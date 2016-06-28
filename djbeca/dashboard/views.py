from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy

from djbeca.core.models import Proposal
from djbeca.core.forms import ProposalForm

from djzbar.utils.hr import chair_departments, person_departments
from djzbar.utils.hr import department_divison_chairs
from djzbar.decorators.auth import portal_auth_required
from djzbar.utils.informix import do_sql as do_esql
from djtools.utils.users import in_group


@portal_auth_required(
    "Chairs and Deans",
    "Chairs and Deans", reverse_lazy("access_denied")
)
def proposal_list(request):

    if in_group(request.user,"Office of Sponsored Programs"):
        proposals = Proposal.objects.all()
        depts = False
        div = False
    else:
        depts = chair_departments(request.user.id)
        div = depts["div"]
        depts = depts["depts"]
        proposals = Proposal.objects.filter(
            department__in=[ key for key,val in depts.iteritems() ]
        )

    return render_to_response(
        "home.html",
        {
            "proposals":proposals,"home":False,
            "depts":depts,"div":div
        },
        context_instance=RequestContext(request)
    )


@portal_auth_required(
    "Chairs and Deans",
    "Chairs and Deans", reverse_lazy("access_denied")
)
def proposal_detail(request, pid):

    proposal = Proposal.objects.get(id=pid)

    return render_to_response(
        "detail.html",
        {"proposal":proposal},
        context_instance=RequestContext(request)
    )

