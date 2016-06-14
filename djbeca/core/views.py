from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy

from djbeca.core.forms import ProposalForm

from djzbar.utils.hr import person_departments
from djzbar.utils.hr import department_divison_chairs
from djzbar.decorators.auth import portal_auth_required
from djtools.utils.mail import send_mail

import logging
logger = logging.getLogger(__name__)


@portal_auth_required(
    "carthageFacultyStatus",
    "carthageFacultyStatus", reverse_lazy("access_denied")
)
def index(request):
    if settings.DEBUG:
        TO_LIST = [settings.ADMINS[0][1],]
    else:
        TO_LIST = [settings.PROPOSAL_EMAIL,]
    BCC = settings.MANAGERS

    depts = person_departments(request.user.id)
    if request.method=='POST':
        form = ProposalForm(depts, request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.user = request.user
            data.save()
            subject = "[OSP Proposal] {}: {}, {}".format(
                data.title, data.user.last_name, data.user.first_name
            )
            chairs = department_divison_chairs(data.department)
            if not settings.DEBUG:
                # Department chair's email
                TO_LIST.append(chairs[0][4])
                # Division chair's email
                TO_LIST.append(chairs[0][8])
            else:
                data.chairs = chairs
            # temporarily assign department to full name
            data.department = chairs[0][0]
            send_mail(
                request, TO_LIST, subject, data.user.email,
                "proposal/email.html", data, BCC
            )
            return HttpResponseRedirect(
                reverse_lazy("proposal_success")
            )
    else:
        form = ProposalForm(depts)
    return render_to_response(
        "proposal/form.html",
        {"form": form,},
        context_instance=RequestContext(request)
    )
