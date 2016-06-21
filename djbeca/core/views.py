from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required

from djbeca.core.models import Proposal
from djbeca.core.forms import ProposalForm

from djzbar.utils.hr import person_departments
from djzbar.utils.hr import department_divison_chairs
from djzbar.decorators.auth import portal_auth_required
from djtools.utils.mail import send_mail


@login_required
def home(request):

    proposals = Proposal.objects.filter(user=request.user)

    return render_to_response(
        "home.html",
        {"proposals":proposals,"home":True,},
        context_instance=RequestContext(request)
    )


@login_required
def proposal_form(request, pid=None):
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

            # division and departmental chairs
            chairs = department_divison_chairs(data.department)
            data.chairs = chairs
            if len(chairs) > 0:
                # temporarily assign department to full name
                data.department = chairs[0][0]
                if not settings.DEBUG:
                    # Department chair's email
                    TO_LIST.append(chairs[0][4])
                    # Division chair's email
                    TO_LIST.append(chairs[0][8])
            else:
                # staff do not have chairs
                data.department = depts[0][1]

            # send the email
            subject = "[OSP Proposal] {}: {}, {}".format(
                data.title, data.user.last_name, data.user.first_name
            )
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


@login_required
def proposal_detail(request, pid):

    proposal = Proposal.objects.get(id=pid)
    if proposal.user != request.user:
        raise Http404

    return render_to_response(
        "detail.html",
        {"proposal":proposal},
        context_instance=RequestContext(request)
    )
