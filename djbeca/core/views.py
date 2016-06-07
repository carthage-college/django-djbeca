from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy

from djbeca.core.forms import ProposalForm

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
        TO_LIST = [settings.SERVER_EMAIL,]
    else:
        TO_LIST = [settings.PROPOSAL_EMAIL,]
    BCC = settings.MANAGERS

    if request.method=='POST':
        form = ProposalForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save()
            email = settings.DEFAULT_FROM_EMAIL
            if data.email:
                email = data.email
            subject = "[Proposal] {} {}".format(
                data.last_name,data.first_name
            )
            send_mail(
                request,TO_LIST, subject, email,"proposal/email.html", data, BCC
            )
            return HttpResponseRedirect(
                reverse_lazy("proposal_success")
            )
    else:
        form = ProposalForm()
    return render_to_response(
        "proposal/form.html",
        {"form": form,},
        context_instance=RequestContext(request)
    )
