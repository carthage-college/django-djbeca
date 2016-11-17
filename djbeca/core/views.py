from django.conf import settings
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse_lazy

from djbeca.core.models import FundingIdentified, FundingPursued, Proposal
from djbeca.core.forms import FundingIdentifiedForm
from djbeca.core.forms import FundingPursuedForm
from djbeca.core.forms import ProposalForm
from djbeca.core.forms import ProposalUpdateForm
from djzbar.utils.hr import chair_departments

from djzbar.utils.hr import person_departments
from djzbar.utils.hr import department_division_chairs
from djzbar.decorators.auth import portal_auth_required
from djtools.utils.mail import send_mail
from djtools.utils.users import in_group


@portal_auth_required(
    session_var="DJBECA_AUTH", redirect_url=reverse_lazy("access_denied")
)
def home(request):
    user = request.user
    depts = False
    div = False
    home = True
    dean_chair = department_division_chairs(
        '(DTID.id={} or DVID.id={})'.format(user.id,user.id)
    )
    if in_group(user,"Office of Sponsored Programs"):
        proposals = Proposal.objects.all()
    elif dean_chair:
        chair_depts = chair_departments(user.id)
        div = chair_depts[2]
        depts = chair_depts[0]
        proposals = Proposal.objects.filter(
            department__in=[ key for key,val in depts['depts'].iteritems() ]
        )
        home = False
    else:
        proposals = Proposal.objects.filter(user=user)

    return render_to_response(
        "home.html",
        {
            "proposals":proposals,"home":home,
            "depts":depts,"div":div
        },
        context_instance=RequestContext(request)
    )


@portal_auth_required(
    session_var="DJBECA_AUTH", redirect_url=reverse_lazy("access_denied")
)
def funding_form(request, pid):

    proposal = get_object_or_404(Proposal, id=pid)
    depts = person_departments(request.user.id)

    if request.method=='POST':
        form_proposal_update = ProposalUpdateForm(
            depts, request.POST, instance=proposal
        )
        form_funding_pursued = FundingPursuedForm(
            request.POST, prefix="ffp", instance=proposal.funding_pursued
        )
        form_funding_identified = FundingIdentifiedForm(
            request.POST, instance=proposal.funding_identified
        )

        if form_proposal_update.is_valid():
            proposal = form_proposal_update.save(commit=False)
            if proposal.funding_status == 'Pursuit of Funding':
                form_funding = form_funding_pursued
            else:
                form_funding = form_funding_identified
            if form_funding.is_valid():
                funding = form_funding.save()
                if proposal.funding_status == "Pursuit of Funding":
                    proposal.funding_pursued = funding
                else:
                    proposal.funding_identified = funding
                proposal.save()

                '''
                # send the email
                subject = "[OSP Program Idea] {}, {}".format(
                    data.user.last_name, data.user.first_name
                )
                send_mail(
                    request, TO_LIST, subject, data.user.email,
                    "proposal/email_approve.html", data, BCC
                )
                # send confirmation to individual submitting idea
                subject = "[OSP Program Idea] {}".format(
                    data.title
                )
                send_mail(
                    request, [data.user.email], subject, settings.PROPOSAL_EMAIL,
                    "proposal/email_confirmation.html", data, BCC
                )
                '''
                return HttpResponseRedirect(
                    reverse_lazy("funding_success")
                )
    else:
        form_proposal_update = ProposalUpdateForm(depts, instance=proposal)
        form_funding_pursued = FundingPursuedForm(
            prefix="ffp", instance=proposal.funding_pursued
        )
        form_funding_identified = FundingIdentifiedForm(
            instance=proposal.funding_identified
        )

    return render_to_response(
        "funding/form.html",
        {
            "proposal":proposal,
            "form_proposal": form_proposal_update,
            "form_funding_identified": form_funding_identified,
            "form_funding_pursued": form_funding_pursued,
        },
        context_instance=RequestContext(request)
    )


@portal_auth_required(
    session_var="DJBECA_AUTH", redirect_url=reverse_lazy("access_denied")
)
def proposal_form(request):
    TO_LIST = [settings.PROPOSAL_EMAIL,]
    BCC = settings.MANAGERS

    depts = person_departments(request.user.id)
    if request.method=='POST':
        form = ProposalForm(depts, request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.user = request.user
            data.save()

            # send email to division dean and departmental chair
            where = 'PT.pcn_03 = "{}"'.format(data.department)
            chairs = department_division_chairs(where)
            if len(chairs) > 0:
                # temporarily assign department to full name
                data.department = chairs[0][0]
                if not settings.DEBUG:
                    # Department chair's email
                    TO_LIST.append(chairs[0][4])
                    # Division dean's email
                    TO_LIST.append(chairs[0][8])
                else:
                    data.chairs = chairs
            else:
                # staff do not have chairs
                data.department = depts[0][1]

            # send the email
            subject = "[OSP Program Idea] {}, {}".format(
                data.user.last_name, data.user.first_name
            )
            send_mail(
                request, TO_LIST, subject, data.user.email,
                "proposal/email_approve.html", data, BCC
            )
            # send confirmation to individual submitting idea
            subject = "[OSP Program Idea] {}".format(
                data.title
            )
            send_mail(
                request, [data.user.email], subject, settings.PROPOSAL_EMAIL,
                "proposal/email_confirmation.html", data, BCC
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


@portal_auth_required(
    session_var="DJBECA_AUTH", redirect_url=reverse_lazy("access_denied")
)
def proposal_detail(request, pid):

    proposal = Proposal.objects.get(id=pid)
    if proposal.user != request.user:
        raise Http404

    return render_to_response(
        "detail.html",
        {"proposal":proposal},
        context_instance=RequestContext(request)
    )
