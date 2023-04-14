# -*- coding: utf-8 -*-

"""Views for all requests."""

import json
from datetime import datetime
from decimal import Decimal
from re import sub

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from djauth.decorators import portal_auth_required
from djbeca.core import forms
from djbeca.core.choices import BUDGET_FUNDING_SOURCE
from djbeca.core.choices import BUDGET_FUNDING_STATUS
from djbeca.core.models import Proposal
from djbeca.core.models import ProposalApprover
from djbeca.core.models import ProposalBudget
from djbeca.core.models import ProposalBudgetFunding
from djbeca.core.models import ProposalContact
from djbeca.core.models import ProposalImpact
from djbeca.core.utils import get_proposals
from djtools.utils.mail import send_mail
from djtools.utils.users import in_group
from djtools.utils.workday import department_person
from djtools.utils.workday import department_all
from djtools.utils.workday import get_managers


DEBUG = settings.DEBUG
REQUIRED_ATTRIBUTE = settings.REQUIRED_ATTRIBUTE
OSP_GROUP = settings.OSP_GROUP

VEEP = User.objects.filter(groups__name=settings.CFO_GROUP)[0]
PROVOST = User.objects.filter(groups__name=settings.PROVOST_GROUP)[0]
PRESIDENT = User.objects.filter(groups__name=settings.PRESIDENT_GROUP)[0]

PROPOSAL_EMAIL_LIST = settings.PROPOSAL_EMAIL_LIST
SERVER_EMAIL = settings.SERVER_EMAIL
TEST_EMAILS = [settings.MANAGERS[0][1], PROPOSAL_EMAIL_LIST[0]]

if DEBUG:
    bcc = TEST_EMAILS
else:
    bcc = settings.PROPOSAL_EMAIL_LIST
    bcc.append(settings.MANAGERS[0][1])


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def home(request):
    """Dashboard home page view."""
    user = request.user
    group = in_group(user, OSP_GROUP)
    if user.is_authenticated:
        proposals = get_proposals(user)
        response = render(
            request,
            'home.html',
            {
                'proposals': proposals['objects'],
                'dean': proposals['dean'],
                'group': group,
            },
        )
    else:
        response = HttpResponseRedirect(reverse_lazy('auth_login'))

    return response


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def impact_form(request, pid):
    """Proposal Form Part B view."""
    proposal = get_object_or_404(Proposal, pk=pid)
    user = request.user
    perms = proposal.permissions(user)

    # we do not allow PIs to update their proposals after save-submit
    # but OSP can do so
    group = in_group(user, OSP_GROUP)
    if (user != proposal.user and not group) or \
       (proposal.save_submit and user == proposal.user) or \
       (proposal.decline and user == proposal.user) or \
       (proposal.closed and user == proposal.user) or \
       (proposal.closed or proposal.decline and group):

        return HttpResponseRedirect(reverse_lazy('home'))

    # budget
    try:
        budget = proposal.budget
    except ProposalBudget.DoesNotExist:
        budget = None
    # budget funding sources: an empty item for new impact form.
    sources = ['']
    if budget:
        sources = budget.funding.all()

    # impact
    try:
        impact = proposal.impact
    except ProposalImpact.DoesNotExist:
        impact = None

    # documents
    docs = [None, None, None]
    for counter, doc in enumerate(proposal.documents.all()):
        docs[counter] = doc

    if request.method == 'POST':
        # budget funding sources
        sources = []
        sids = request.POST.getlist('sid[]')
        amount = request.POST.getlist('amount[]')
        source = request.POST.getlist('source[]')
        status = request.POST.getlist('status[]')
        for count, _ in enumerate(sids):
            # skip doop-master container
            if count != 0:
                sources.append({
                    'amount': amount[count],
                    'source': source[count],
                    'status': status[count],
                })

        form_impact = forms.ImpactForm(
            request.POST,
            instance=impact,
            label_suffix='',
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )
        form_budget = forms.BudgetForm(
            request.POST,
            request.FILES,
            instance=budget,
            prefix='budget',
            label_suffix='',
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )
        form_comments = forms.CommentsForm(
            request.POST,
            prefix='comments',
            label_suffix='',
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )
        form_doc1 = forms.DocumentForm(
            request.POST,
            request.FILES,
            instance=docs[0],
            prefix='doc1',
            label_suffix='',
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )
        form_doc2 = forms.DocumentForm(
            request.POST,
            request.FILES,
            instance=docs[1],
            prefix='doc2',
            label_suffix='',
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )
        form_doc3 = forms.DocumentForm(
            request.POST,
            request.FILES,
            instance=docs[2],
            prefix='doc3',
            label_suffix='',
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )

        valid = (
            form_impact.is_valid() and
            form_budget.is_valid() and
            form_doc1.is_valid() and
            form_doc2.is_valid() and
            form_doc3.is_valid()
        )
        if valid:
            # proposal impact
            impact = form_impact.save(commit=False)
            impact.proposal = proposal
            impact.save()
            # m2m save for GenericChoice relationships
            form_impact.save_m2m()
            # set proposal opened to False if it was True
            if proposal.opened:
                proposal.opened = False
            # proposal budget
            budget = form_budget.save(commit=False)
            budget.proposal = proposal
            budget.save()
            # remove deleted budget funding sources
            sources_list = [source.id for source in budget.funding.all()]
            dif = set(sources_list).difference(sids)
            if dif:
                for sid_dif in list(dif):
                    funding = ProposalBudgetFunding.objects.get(pk=sid_dif)
                    funding.delete()
            # add or update budget funding sources
            for index, _ in enumerate(sids):
                # skip doop-master container
                if index != 0:
                    if sids[index]:
                        fid = int(sids[int(index)])
                    else:
                        fid = None
                    try:
                        funding = ProposalBudgetFunding.objects.get(pk=fid)
                    except ProposalBudgetFunding.DoesNotExist:
                        funding = ProposalBudgetFunding()
                        funding.budget = budget
                    if amount[index]:
                        # strip any non-numeric characters
                        funding_amount = 0
                        try:
                            funding_amount = Decimal(sub(r'[^\d.]', '', amount[index]))
                        except Exception:
                            pass
                        funding.amount = funding_amount
                    funding.source = source[index]
                    funding.status = status[index]
                    funding.save()
            # proposal comments (not a ModelForm)
            if request.POST.get('comments-comments'):
                form_comments.is_valid()
                comments = form_comments.cleaned_data
                proposal.comments = comments['comments']

            # document 1
            doc1 = form_doc1.save(commit=False)
            doc1.proposal = proposal
            doc1.save()
            # document 2
            doc2 = form_doc2.save(commit=False)
            doc2.proposal = proposal
            doc2.save()
            # document 3
            doc3 = form_doc3.save(commit=False)
            doc3.proposal = proposal
            doc3.save()

            # Send email to Approvers and Division Dean if the PI is finished
            # with the proposal
            # (i.e. hits 'submit-save' rather than 'save and continue')
            post = request.POST
            if post.get('save_submit') and not proposal.save_submit:
                # set the save submit flag so PI cannot update
                proposal.save_submit = True
                proposal.save()
                # email approvers
                subject = (
                    'Routing & Authorization Form Part B: '
                    'Your Approval Needed for "{0}" by {1}, {2}'
                ).format(
                    proposal.title,
                    proposal.user.last_name,
                    proposal.user.first_name,
                )
                to_list = []
                for approver in proposal.approvers.all():
                    to_list.append(approver.user.email)
                if DEBUG:
                    proposal.to_list = to_list
                    to_list = TEST_EMAILS

                if to_list:
                    # send the email to Approvers
                    send_mail(
                        request,
                        to_list,
                        subject,
                        proposal.user.email,
                        'impact/email_approve_approvers.html',
                        proposal,
                        bcc,
                    )


                # email Division Dean (level3)
                where = 'dept_table.dept = "{0}"'.format(proposal.department)
                for dean in get_managers('deans'):
                    for dept in dean['departments_managed']:
                        if dept == proposal.department:
                            pass


                # staff do not have deans so no need to send email
                if deans:
                    subject = (
                        'Review and Provide Final Authorization for PART B: '
                        '"{0}" by {1}, {2}'
                    ).format(
                        proposal.title,
                        proposal.user.last_name,
                        proposal.user.first_name,
                    )
                    # we need department code in email e.g. MUS
                    proposal.department_name = chairs[0][0]
                    # Division dean's email
                    to_list = [chairs[0][10]]
                    if DEBUG:
                        proposal.to_list = to_list
                        to_list = TEST_EMAILS

                    # send the email
                    send_mail(
                        request,
                        to_list,
                        subject,
                        proposal.user.email,
                        'impact/email_approve_level3.html',
                        proposal,
                        bcc,
                    )

                # send confirmation to the Primary Investigator (PI)
                # who submitted the form
                subject = "[Part B] Submission Received: {0}".format(
                    proposal.title,
                )

                to_list = [proposal.user.email]
                if DEBUG:
                    proposal.to_list = to_list
                    to_list = TEST_EMAILS

                # send the email
                send_mail(
                    request,
                    to_list,
                    subject,
                    PROPOSAL_EMAIL_LIST[0],
                    'impact/email_confirmation.html',
                    proposal,
                    bcc,
                )
                return HttpResponseRedirect(reverse_lazy('impact_success'))
            else:
                proposal.save()
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "Your proposal data have been saved.",
                    extra_tags='success',
                )
                return HttpResponseRedirect(
                    reverse_lazy('impact_form', kwargs={'pid': proposal.id}),
                )
    else:
        form_impact = forms.ImpactForm(
            instance=impact,
            label_suffix='',
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )
        form_budget = forms.BudgetForm(
            instance=budget,
            prefix='budget',
            label_suffix='',
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )
        form_comments = forms.CommentsForm(
            initial={'comments': proposal.comments},
            prefix='comments',
            label_suffix='',
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )
        form_doc1 = forms.DocumentForm(
            instance=docs[0],
            prefix='doc1',
            label_suffix='',
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )
        form_doc2 = forms.DocumentForm(
            instance=docs[1],
            prefix='doc2',
            label_suffix='',
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )
        form_doc3 = forms.DocumentForm(
            instance=docs[2],
            prefix='doc3',
            label_suffix='',
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )

    return render(
        request,
        'impact/form.html',
        {
            'funding_source': BUDGET_FUNDING_SOURCE,
            'funding_status': BUDGET_FUNDING_STATUS,
            'form_budget': form_budget,
            'form_comments': form_comments,
            'form_impact': form_impact,
            'form_doc1': form_doc1,
            'form_doc2': form_doc2,
            'form_doc3': form_doc3,
            'osp': group,
            'perms': perms,
            'sources': sources,
        },
    )


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def proposal_form(request, pid=None):
    """Proposal Form Part A view."""
    investi = None
    proposal = None
    perms = None
    user = request.user
    group = in_group(user, OSP_GROUP)

    if pid:
        proposal = get_object_or_404(Proposal, pk=pid)
        perms = proposal.permissions(user)

        # we do not allow anyone but the PI to update a proposal
        if proposal.user != user and not group:
            return HttpResponseRedirect(reverse_lazy('home'))
        # we do not allow PIs to update their proposals after save-submit
        # but OSP can do so
        elif proposal.save_submit and not group:
            return HttpResponseRedirect(reverse_lazy('home'))
        elif (not proposal.level3 or not proposal.opened) and not group:
            return HttpResponseRedirect(reverse_lazy('home'))
        elif (proposal.decline or proposal.closed) and not group:
            return HttpResponseRedirect(reverse_lazy('home'))
        else:
            investigators = proposal.contact.filter(
                tags__name='Co-Principal Investigators',
            )
    if group:
        depts = department_all(choices=True)
    else:
        depts = department_person(user.id, choices=True)
    if request.method == 'POST':
        form = forms.ProposalForm(
            depts,
            request.POST,
            instance=proposal,
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )
        form_investi = forms.InvestigatorsForm(
            request.POST,
            prefix='investi',
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )
        if form.is_valid():
            data = form.save(commit=False)
            # we don't want to change ownership if someone else with
            # permission is updating the proposal
            if not proposal:
                data.user = user
            data.save()

            form_investi.is_valid()

            # delete the old objects because it's just easier this way
            if proposal:
                if investigators:
                    investigators.delete()
            # obtain our new set of contacts
            investigators = form_investi.cleaned_data
            for insti in list(range(1, 6)):
                investigator = ProposalContact(
                    proposal=data,
                    name=investigators['name{0}'.format(insti)],
                    institution=investigators['institution{0}'.format(insti)],
                )
                investigator.save()
                investigator.tags.add('Co-Principal Investigators')

            # send emails only if we have a new proposal or a revised proposal
            if not proposal or data.opened:
                where = 'dept_table.dept = "{0}"'.format(data.department)
                chairs = department_division_chairs(where)
                to_list = []
                # add approvers to distribution list
                for approver in data.approvers.all():
                    to_list.append(approver.user.email)

                if len(chairs) > 0:
                    # we need department full name in email
                    data.department_name = chairs[0][0]
                    # Division dean's email
                    to_list.append(chairs[0][10])
                    if DEBUG:
                        data.to_list = to_list
                        to_list = TEST_EMAILS
                else:
                    # staff do not have a dean so we send the email
                    # to OSP folks
                    to_list.append(PROPOSAL_EMAIL_LIST)
                    if DEBUG:
                        data.to_list = to_list
                        to_list = TEST_EMAILS

                    # for display purposes only in the email
                    #data.department_name = depts[0][1]

                # if proposal has been reopened, we set opened to False
                # so that proposal now is considered a new attempt at approval
                data.opened = False
                data.save()
                # set OSP status for editing email content
                data.osp = group

                # send the email to Dean or OSP
                subject = 'Review and Authorization Required for Part A: \
                    Your Approval Needed for "{0}" by {1}, {2}'.format(
                    data.title, data.user.last_name, data.user.first_name,
                )
                if not data.save_submit:
                    send_mail(
                        request,
                        to_list,
                        subject,
                        PROPOSAL_EMAIL_LIST[0],
                        'proposal/email_approve.html',
                        data,
                        bcc,
                    )
                # send confirmation to the Primary Investigator (PI)
                # who submitted the form
                subject = "Part A Submission Received: {0}".format(data.title)

                if DEBUG:
                    to_list = TEST_EMAILS
                    data.to_list = data.user.email
                else:
                    to_list = [data.user.email]

                # OSP can update proposals after save/submit
                if not data.save_submit:
                    send_mail(
                        request,
                        to_list,
                        subject,
                        PROPOSAL_EMAIL_LIST[0],
                        'proposal/email_confirmation.html',
                        data,
                        bcc,
                    )
                return HttpResponseRedirect(reverse_lazy('proposal_success'))
            else:
                # set the data saved message
                # and redirect to proposal form
                messages.add_message(
                    request,
                    messages.SUCCESS,
                    "Your proposal data have been saved.",
                    extra_tags='success',
                )
                return HttpResponseRedirect(
                    reverse_lazy(
                        'proposal_update', kwargs={'pid': proposal.id},
                    ),
                )
    else:
        form = forms.ProposalForm(
            depts,
            instance=proposal,
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )

        if proposal:
            investi = {}
            for count1, igor in enumerate(investigators, 1):
                investi['institution{0}'.format(count1)] = igor.institution
                investi['name{0}'.format(count1)] = igor.name

        form_investi = forms.InvestigatorsForm(
            initial=investi,
            prefix='investi',
            use_required_attribute=REQUIRED_ATTRIBUTE,
        )
    if group:
        depts = department_all()
    else:
        depts = department_person(user.id)
    return render(
        request,
        'proposal/form.html',
        {
            'form': form,
            'perms': perms,
            'form_investi': form_investi,
            'osp': group,
            'depts': depts,
        },
    )


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def proposal_detail(request, pid):
    """Proposal detail view."""
    proposal = get_object_or_404(Proposal, pk=pid)
    user = request.user

    # verify that the user can view this proposal
    # and if they are an approver or not
    perms = proposal.permissions(user)
    if not perms['view']:
        raise Http404

    co_principals = proposal.contact.filter(
        tags__name='Co-Principal Investigators',
    )

    try:
        form_impact = forms.ImpactForm(
            instance=proposal.impact, label_suffix='',
        )
    except ProposalImpact.DoesNotExist:
        form_impact = None

    excludes = [
        'id',
        'created_at',
        'updated_at',
        'proposal',
        'level3',
        'level2',
        'level1',
        'admin_comments',
        'disclosure_assurance',
    ]

    return render(
        request,
        'proposal/detail.html',
        {
            'proposal': proposal,
            'co_principals': co_principals,
            'perms': perms,
            'impacts': form_impact,
            'excludes': excludes,
        },
    )


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def proposal_approver(request, pid=0):
    """Add an approver to a proposal."""
    #
    # OJO: we still need to validate that a Dean can add an approver
    # to the proposal but we can trust deans for now.

    user = request.user
    if in_group(user, OSP_GROUP) or get_managers('deans', user.id):
        proposal = None
        proposal = get_object_or_404(Proposal, pk=pid)
        if request.method == 'POST':
            form = forms.ProposalApproverForm(
                request.POST,
                use_required_attribute=REQUIRED_ATTRIBUTE,
            )
            if form.is_valid():
                cd = form.cleaned_data
                user = User.objects.get(pk=cd['user'])
                approver = ProposalApprover(user=user, proposal=proposal)
                # in the future, users might be able to select the role
                # that an approver might replace but for now we handle it
                # here and by default in the model, which is 'level3'.
                # if the proposal is from faculty, the approver does not
                # replace level3 so replace is set to None.
                did = proposal.department_name
                for dept in department_all():
                    if dept['id'] == did and dept['orbit'] == 'faculty':
                        approver.replace = None
                        approver.save()
                        break

                # send an email to approver
                prefix = 'Your Review and Authorization Required'
                subject = '{0}: "{1}" by {2}, {3}'.format(
                    prefix,
                    proposal.title,
                    proposal.user.last_name,
                    proposal.user.first_name,
                )

                if DEBUG:
                    to_list = TEST_EMAILS
                    proposal.to_list = [
                        proposal.user.email, approver.user.email,
                    ]
                else:
                    to_list = [approver.user.email]

                send_mail(
                    request,
                    to_list,
                    subject,
                    PROPOSAL_EMAIL_LIST[0],
                    'approver/email.html',
                    {'proposal': proposal},
                    bcc,
                )

                return HttpResponseRedirect(
                    reverse_lazy('approver_success'),
                )

        else:
            form = forms.ProposalApproverForm(
                initial={'proposal': pid},
                use_required_attribute=REQUIRED_ATTRIBUTE,
            )

        return render(
            request,
            'approver/form.html',
            {'proposal': proposal, 'form': form},
        )
    else:
        return HttpResponseRedirect(reverse_lazy('home'))


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def email_investigator(request, pid, action):
    """Send an email to the primary investigator."""
    form_data = None
    proposal = get_object_or_404(Proposal, pk=pid)
    if request.method == 'POST':
        form = forms.EmailInvestigatorForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            if 'execute' in request.POST:
                if DEBUG:
                    to_list = TEST_EMAILS
                else:
                    to_list = [proposal.user.email]
                send_mail(
                    request,
                    to_list,
                    "[Office of Sponsored Programs] Grant Proposal: {0}".format(
                        proposal.title,
                    ),
                    request.user.email,
                    'investigator/email_data.html',
                    {'content': form_data['content']},
                    bcc,
                )
                return HttpResponseRedirect(
                    reverse_lazy('email_investigator_success'),
                )
            else:
                return render(
                    request,
                    'investigator/email_form.html',
                    {'form': form, 'data': form_data, 'p': proposal},
                )
    else:
        form = forms.EmailInvestigatorForm()

    return render(
        request,
        'investigator/email_form.html',
        {'form': form, 'data': form_data, 'p': proposal, 'action': action},
    )


@csrf_exempt
@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def proposal_status(request):
    """Set the status on a proposal."""
    # options:  approve, decline, open, close, needs work
    # method:   AJAX POST

    # requires POST request
    if request.POST:
        pid = request.POST.get('pid')
        try:
            pid = int(pid)
        except ValueError:
            return HttpResponse("Access Denied")
        user = request.user
        proposal = get_object_or_404(Proposal, pk=pid)
        try:
            impact = proposal.impact
        except ProposalImpact.DoesNotExist:
            impact = None
        perms = proposal.permissions(user)
        # if user does not have 'approve' permissions, we can stop here,
        # regardless of whether we are approving/declining, closing/opening,
        # or indicating that the proposal "needs work".
        if not perms['approve'] and not perms['open']:
            return HttpResponse("Access Denied")
        else:
            status = request.POST.get('status')
            if not status:
                return HttpResponse("No status")

            # close
            if status == 'close':
                if perms['close']:
                    proposal.closed = True
                    proposal.opened = False
                    proposal.decline = False
                    proposal.level3 = False
                    proposal.email_approved = False
                    proposal.save_submit = False
                    proposal.save()
                    # we might not have a proposal impact relationship
                    if impact:
                        proposal.impact.disclosure_assurance = False
                        proposal.impact.level3 = False
                        proposal.impact.level2 = False
                        proposal.impact.level1 = False
                        proposal.impact.save()
                    # Approvers
                    for approver in proposal.approvers.all():
                        approver.step1 = False
                        approver.step2 = False
                        approver.save()
                    return HttpResponse("Proposal has been closed")
                else:
                    return HttpResponse("You do not have permission to close")

            # open
            if status == 'open':
                if perms['open']:
                    # Approvers
                    for approver in proposal.approvers.all():
                        if not proposal.step1() and not proposal.closed:
                            approver.step1 = False
                        if proposal.step1() and not proposal.closed:
                            approver.step2 = False
                        approver.save()
                    # reset booleans back to False
                    if not proposal.step1() and not proposal.closed:
                        proposal.level3 = False
                    proposal.closed = False
                    proposal.opened = True
                    proposal.decline = False
                    proposal.email_approved = False
                    proposal.save_submit = False
                    proposal.proposal_type = 'resubmission'
                    proposal.save()
                    # we might not have a proposal impact relationship
                    if proposal.step1() and impact:
                        proposal.impact.disclosure_assurance = False
                        proposal.impact.level3 = False
                        proposal.impact.level2 = False
                        proposal.impact.level1 = False
                        proposal.impact.save()

                    return HttpResponse("Proposal has been reopened")
                else:
                    return HttpResponse("You do not have permission to open")

            # find out on which step we are
            decline_template = 'impact/email_decline.html'
            decline_subject = 'Part B: Not approved, requires \
                additional clarrification: "{0}"'.format(proposal.title)
            needs_work_template = 'impact/email_needswork.html'
            needs_work_subject = 'Part B: Needs work, requires \
                additional clarrification: "{0}"'.format(proposal.title)
            if not proposal.step1():
                step = 'step1'
                decline_template = 'proposal/email_decline.html'
                decline_subject = 'Part A: Not approved, requires \
                    additonal clarrification: "{0}"'.format(proposal.title)
                needs_work_template = 'proposal/email_needswork.html'
                needs_work_subject = 'Part A: Needs work, requires \
                    additonal clarrification: "{0}"'.format(proposal.title)
            elif proposal.step1() and not impact:
                return HttpResponse("Step 2 has not been initiated")
            elif impact and not proposal.save_submit:
                return HttpResponse("Step 2 has not been completed")
            else:
                step = 'step2'

            # anyone can decline, for now. i suspect that will change
            # and thus the data model will have to change.
            if status == 'decline':
                if perms['decline']:
                    # Proposal object
                    proposal.decline = True
                    proposal.opened = False
                    proposal.email_approved = False
                    proposal.save_submit = False
                    if step == 'step1':
                        proposal.level3 = False
                    proposal.save()
                    # ProposalImpact object
                    if step == 'step2':
                        proposal.impact.level1 = False
                        proposal.impact.level2 = False
                        proposal.impact.level3 = False
                        proposal.impact.disclosure_assurance = False
                        proposal.impact.save()
                    # Approvers
                    for approver in proposal.approvers.all():
                        if approver.user == user:
                            if step == 'step1':
                                approver.step1 = False
                            else:
                                approver.step2 = False
                            approver.save()
                            break
                    # send email to PI
                    to_list = [proposal.user.email]
                    if DEBUG:
                        proposal.to_list = to_list
                        to_list = TEST_EMAILS
                    send_mail(
                        request,
                        to_list,
                        decline_subject,
                        user.email,
                        decline_template,
                        proposal,
                        bcc,
                    )
                    return HttpResponse("Proposal Declined")
                else:
                    return HttpResponse("You don't have permission to decline")

            # we can stop here if 'needs work', just like decline.
            if status == 'needswork':
                if perms['needswork']:
                    # Proposal object
                    proposal.decline = False
                    proposal.closed = False
                    proposal.opened = True
                    proposal.email_approved = False
                    proposal.save_submit = False
                    proposal.proposal_type = 'revised'
                    if step == 'step1':
                        proposal.level3 = False
                    proposal.save()
                    # ProposalImpact object
                    if step == 'step2':
                        proposal.impact.level1 = False
                        proposal.impact.level2 = False
                        proposal.impact.level3 = False
                        proposal.impact.disclosure_assurance = False
                        proposal.impact.save()
                    # Approvers
                    for approver in proposal.approvers.all():
                        if step == 'step1':
                            approver.step1 = False
                        else:
                            approver.step2 = False
                        approver.save()
                        break

                    to_list = [proposal.user.email]
                    if DEBUG:
                        proposal.to_list = to_list
                        to_list = TEST_EMAILS
                    send_mail(
                        request,
                        to_list,
                        needs_work_subject,
                        user.email,
                        needs_work_template,
                        proposal,
                        bcc,
                    )
                    return HttpResponse('Proposal "needs work" email sent')
                else:
                    return HttpResponse("Permission denied")

            #
            # begin approve logic
            #

            # default email subject
            subject = '{0}: "{1}"'.format(
                'You are Approved to begin Part B',
                proposal.title,
            )

            # establish the email distribution list
            to_list = [proposal.user.email]
            if DEBUG:
                proposal.to_list = to_list
                to_list = TEST_EMAILS

            # default message for when none of the conditions below are met
            message = "You do not have permission to '{}'".format(status)

            # if step1 and Division Dean
            if step == 'step1' and perms['level3']:
                proposal.level3 = True
                proposal.save()
                # send email to PI informing them that they are approved
                # to begin Part B
                send_mail(
                    request,
                    to_list,
                    subject,
                    proposal.user.email,
                    'proposal/email_authorized.html',
                    proposal,
                    bcc,
                )
                message = "Dean/VP approved Part A"
            # if step2 and Division Dean
            elif step == 'step2' and perms['level3']:
                proposal.impact.level3 = True
                proposal.impact.save()
                message = "Division Dean approved Part B"
                # send email to Provost and VP for Business informing
                # them that the Division Dean has approved Part B
                # and the proposal is awaiting their approval.
                if proposal.ready_level1():
                    to_list = [VEEP.email, PROVOST.email]
                    if DEBUG:
                        proposal.to_list = to_list
                        to_list = TEST_EMAILS
                    subject = 'Review and Provide Final Authorization for PART B: "{0}" by {1}, {2}'.format(
                        proposal.title,
                        proposal.user.last_name,
                        proposal.user.first_name,
                    )
                    send_mail(
                        request,
                        to_list,
                        subject,
                        PROPOSAL_EMAIL_LIST[0],
                        'impact/email_approve_level1.html',
                        proposal,
                        bcc,
                    )
            # VP for Business?
            elif user.id == VEEP.id and step == 'step2':
                proposal.impact.level2 = True
                try:
                    approver = proposal.approvers.get(user=user)
                    proposal.impact.level3 = True
                    # send email to Provost to approve Part B because VEEP
                    # was both level3 and level2 approver and provost has
                    # not been notified yet.
                    to_list = [PROVOST.email]
                    subject = 'Review and Provide Final Authorization for PART B: "{0}" by {1}, {2}'.format(
                        proposal.title,
                        proposal.user.last_name,
                        proposal.user.first_name,
                    )
                    if DEBUG:
                        proposal.to_list = to_list
                        to_list = TEST_EMAILS
                    send_mail(
                        request,
                        to_list,
                        subject,
                        proposal.user.email,
                        'impact/email_approve_level1.html',
                        proposal,
                        bcc,
                    )
                except ProposalApprover.DoesNotExist:
                    pass
                proposal.impact.save()
                message = "VP for Business approved Part B"
            # Provost?
            elif user.id == PROVOST.id and step == 'step2':
                proposal.impact.level1 = True
                proposal.impact.save()
                message = "Provost approved Part B"
            # awarded
            elif status == 'awarded' and perms['superuser']:
                proposal.awarded = True
                proposal.save()
                message = "Proposal is awarded"
            # approvers
            else:
                try:
                    approver = proposal.approvers.get(user=user)
                    approver.__dict__[step] = True
                    approver.save()
                    # if approver replaces Division Dean set level3 to True
                    if approver.replace == 'level3':
                        if step == 'step1':
                            proposal.level3 = True
                            proposal.save()
                        else:
                            proposal.impact.level3 = True
                            proposal.impact.save()
                    # if step 1 is complete send email notification
                    if (proposal.step1() and step == 'step1'):
                        send_mail(
                            request,
                            to_list,
                            subject,
                            proposal.user.email,
                            'proposal/email_authorized.html',
                            proposal,
                            bcc,
                        )
                    # if step 2 is complete and we are ready for
                    # VP for Business and Provost to weight in, send email
                    if proposal.ready_level1():
                        to_list = [VEEP.email, PROVOST.email]
                        if DEBUG:
                            proposal.to_list = to_list
                            to_list = TEST_EMAILS
                        subject = (
                            'Review & Provide Final Authorization for PART B: '
                            '"{0}" by {1}, {2}'
                        ).format(
                            proposal.title,
                            proposal.user.last_name,
                            proposal.user.first_name,
                        )
                        send_mail(
                            request,
                            to_list,
                            subject,
                            PROPOSAL_EMAIL_LIST[0],
                            'impact/email_approve_level1.html',
                            proposal,
                            bcc,
                        )
                    message = "Approved by {0} {1}".format(
                        approver.user.first_name,
                        approver.user.last_name,
                    )
                except ProposalApprover.DoesNotExist:
                    message = """
                        There was a problem setting the status for this proposal
                    """
    else:
        message = "Requires POST request"

    return HttpResponse(message)


@csrf_exempt
@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def clear_cache(request, ctype='blurbs'):
    """Clear the cache for API content."""
    cid = request.POST.get('cid')
    request_type = 'post'
    if not cid:
        cid = request.GET.get('cid')
        request_type = 'get'
    if cid:
        key = 'livewhale_{0}_{1}'.format(ctype, cid)
        cache.delete(key)
        timestamp = datetime.timestamp(datetime.now())
        earl = '{0}/live/{1}/{2}@JSON?cache={3}'.format(
            settings.LIVEWHALE_API_URL, ctype, cid, timestamp,
        )
        try:
            response = requests.get(earl, headers={'Cache-Control': 'no-cache'})
            text = json.loads(response.text)
            cache.set(key, text)
            api_data = mark_safe(text['body'])
        except ValueError:
            api_data = "Cache was not cleared."
        if request_type == 'post':
            content_type = 'text/plain; charset=utf-8'
        else:
            content_type = 'text/html; charset=utf-8'
    else:
        api_data = "Requires a content ID"

    return HttpResponse(api_data, content_type=content_type)


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def proposal_success(request):
    """Redirect here after user submits Part A."""
    return render(request, 'proposal/done.html')


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def impact_success(request):
    """Redirect here after user submits Part B."""
    return render(request, 'impact/done.html')


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def approver_success(request):
    """Redirect here after user adds an approver to a proposal."""
    return render(request, 'approver/done.html')


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied'),
)
def email_investigator_success(request):
    """Redirect here after user submits an email form."""
    return render(request, 'investigator/email_done.html')
