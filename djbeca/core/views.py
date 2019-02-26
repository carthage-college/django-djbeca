from django.conf import settings
from django.contrib import messages
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404

from djbeca.core.models import Proposal, ProposalApprover, ProposalBudget
from djbeca.core.models import ProposalContact
from djbeca.core.forms import *
from djbeca.core.utils import get_proposals

from djzbar.utils.hr import get_position, person_departments
from djzbar.utils.hr import department_division_chairs
from djzbar.decorators.auth import portal_auth_required

from djtools.utils.mail import send_mail
from djtools.utils.users import in_group
from djtools.fields import NOW

from djauth.LDAPManager import LDAPManager

DEBUG = settings.DEBUG
REQUIRED_ATTRIBUTE = settings.REQUIRED_ATTRIBUTE
OSP_GROUP = settings.OSP_GROUP
DEANS_GROUP = settings.DEANS_GROUP
VEEP = get_position(settings.VEEP_TPOS)
PROVOST = get_position(settings.PROV_TPOS)
PRESIDENT = get_position(settings.PREZ_TPOS)
PROPOSAL_EMAIL_LIST = settings.PROPOSAL_EMAIL_LIST
SERVER_EMAIL = settings.SERVER_EMAIL
MANAGER = settings.MANAGERS[0][1]
if DEBUG:
    BCC = [MANAGER,]
else:
    BCC = settings.PROPOSAL_EMAIL_LIST
    BCC.append(MANAGER)


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied')
)
def home(request):
    '''
    dashboard home page view
    '''

    user = request.user
    group = in_group(user, OSP_GROUP)
    if user.is_authenticated:
        proposals = get_proposals(user)
        return render(
            request, 'home.html',
            {
                'proposals':proposals['objects'],
                'dean_chair':proposals['dean_chair'],
                'group':group,'dc':proposals['dc'],'depts':proposals['depts'],
                'div':proposals['div'],'approver':proposals['approver']
            }
        )
    else:
        return HttpResponseRedirect(reverse_lazy('auth_login'))


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied')
)
def impact_form(request, pid):
    '''
    Proposal Form Part B view
    '''

    proposal = get_object_or_404(Proposal, id=pid)
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

    # budget and impact
    try:
        impact = proposal.proposal_impact
        budget = proposal.proposal_budget
    except:
        impact = budget = None
    # documents
    docs = [None,None,None]
    for c, d in enumerate(proposal.proposal_documents.all()):
        docs[c] = d

    if request.method=='POST':
        form_impact = ImpactForm(
            request.POST, instance=impact, label_suffix='',
            use_required_attribute = REQUIRED_ATTRIBUTE
        )
        form_budget = BudgetForm(
            request.POST, request.FILES,
            instance=budget, prefix='budget', label_suffix='',
            use_required_attribute = REQUIRED_ATTRIBUTE
        )
        form_comments = CommentsForm(
            request.POST, prefix='comments', label_suffix='',
            use_required_attribute = REQUIRED_ATTRIBUTE
        )
        form_doc1 = DocumentForm(
            request.POST, request.FILES,
            instance=docs[0], prefix='doc1', label_suffix='',
            use_required_attribute = REQUIRED_ATTRIBUTE
        )
        form_doc2 = DocumentForm(
            request.POST, request.FILES,
            instance=docs[1], prefix='doc2', label_suffix='',
            use_required_attribute = REQUIRED_ATTRIBUTE
        )
        form_doc3 = DocumentForm(
            request.POST, request.FILES,
            instance=docs[2], prefix='doc3', label_suffix='',
            use_required_attribute = REQUIRED_ATTRIBUTE
        )
        if form_impact.is_valid() and form_budget.is_valid() and \
          form_doc1.is_valid() and form_doc2.is_valid() and \
          form_doc3.is_valid():
            # proposal impact
            impact = form_impact.save(commit=False)
            impact.proposal = proposal
            impact.save()
            # set proposal opened to False if it was True
            if proposal.opened:
                proposal.opened = False
                proposal.save()
            # proposal budget
            budget = form_budget.save(commit=False)
            budget.proposal = proposal
            budget.save()
            # proposal comments (not a ModelForm)
            if request.POST.get('comments-comments'):
                form_comments.is_valid()
                comments = form_comments.cleaned_data
                proposal.comments = comments['comments']
                proposal.save()

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
                    u'Routing & Authorization Form Part B: '
                    'Your Approval Needed for "{}" by {}, {}'
                ).format(
                    proposal.title, proposal.user.last_name,
                    proposal.user.first_name
                )
                to_list = []
                for a in proposal.proposal_approvers.all():
                    to_list.append(a.user.email)
                if DEBUG:
                    proposal.to_list = to_list
                    to_list = [MANAGER]

                if to_list:
                    # send the email to Approvers
                    send_mail(
                        request, to_list, subject, proposal.user.email,
                        'impact/email_approve_approvers.html', proposal, BCC
                    )

                # email Division Dean (level3)
                where = 'PT.pcn_03 = "{}"'.format(proposal.department)
                chairs = department_division_chairs(where)
                # staff do not have deans so len will be 0 in that case
                if len(chairs) > 0:
                    subject = (
                        u'Review and Provide Final Authorization for PART B: '
                        '"{}" by {}, {}'
                    ).format(
                        proposal.title, proposal.user.last_name,
                        proposal.user.first_name
                    )
                    # we need department full name in email
                    proposal.department_name = chairs[0][0]
                    # Division dean's email
                    to_list = [chairs[0][8]]
                    if DEBUG:
                        proposal.to_list = to_list
                        to_list = [MANAGER]

                    # send the email
                    send_mail(
                        request, to_list, subject, proposal.user.email,
                        'impact/email_approve_level3.html', proposal, BCC
                    )

                # send confirmation to the Primary Investigator (PI)
                # who submitted the form
                subject = u"[Part B] Submission Received: {}".format(
                    proposal.title
                )

                to_list = [proposal.user.email]
                if DEBUG:
                    proposal.to_list = to_list
                    to_list = [MANAGER]

                # send the email
                send_mail(
                    request, to_list, subject, PROPOSAL_EMAIL_LIST[0],
                    'impact/email_confirmation.html', proposal, BCC
                )
                return HttpResponseRedirect(
                    reverse_lazy('impact_success')
                )
            else:
                messages.add_message(
                    request, messages.SUCCESS,
                    '''
                    Your proposal data have been saved.
                    ''',
                    extra_tags='success'
                )
                return HttpResponseRedirect(
                    reverse_lazy('impact_form', kwargs={'pid': proposal.id})
                )
    else:
        form_impact = ImpactForm(
            instance=impact, label_suffix='',
            use_required_attribute = REQUIRED_ATTRIBUTE
        )
        form_budget = BudgetForm(
            instance=budget, prefix='budget', label_suffix='',
            use_required_attribute = REQUIRED_ATTRIBUTE
        )
        form_comments = CommentsForm(
            initial={'comments':proposal.comments},
            prefix='comments', label_suffix='',
            use_required_attribute = REQUIRED_ATTRIBUTE
        )
        form_doc1 = DocumentForm(
            instance=docs[0], prefix='doc1', label_suffix='',
            use_required_attribute = REQUIRED_ATTRIBUTE
        )
        form_doc2 = DocumentForm(
            instance=docs[1], prefix='doc2', label_suffix='',
            use_required_attribute = REQUIRED_ATTRIBUTE
        )
        form_doc3 = DocumentForm(
            instance=docs[2], prefix='doc3', label_suffix='',
            use_required_attribute = REQUIRED_ATTRIBUTE
        )

    return render(
        request, 'impact/form.html', {
            'form_budget': form_budget, 'form_comments': form_comments,
            'form_impact': form_impact, 'form_doc1': form_doc1,
            'form_doc2': form_doc2, 'form_doc3': form_doc3, 'perms': perms
        }
    )


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied')
)
def proposal_form(request, pid=None):
    '''
    Proposal Form Part A view
    '''

    institu = None
    investi = None
    proposal = None
    perms = None
    user = request.user

    if pid:
        proposal = get_object_or_404(Proposal, id=pid)
        perms = proposal.permissions(user)
        group = in_group(user, OSP_GROUP)
        # we do not allow anyone but the PI to update a proposal
        if proposal.user != user and not group:
            return HttpResponseRedirect(
                reverse_lazy('home')
            )
        # we do not allow PIs to update their proposals after save-submit
        # but OSP can do so
        elif proposal.save_submit and not group:
            return HttpResponseRedirect(
                reverse_lazy('home')
            )
        elif not proposal.level3 and not proposal.opened:
            return HttpResponseRedirect(
                reverse_lazy('home')
            )
        elif proposal.decline or proposal.closed:
            return HttpResponseRedirect(
                reverse_lazy('home')
            )
        else:
            investigators = proposal.proposal_contact.filter(
                tags__name='Co-Principal Investigators'
            )
            institutions = proposal.proposal_contact.filter(
                tags__name='Other Institution'
            )

    depts = person_departments(user.id)
    if request.method=='POST':
        form = ProposalForm(
            depts, request.POST, instance=proposal
        )
        form_institu = InstitutionsForm(
            request.POST, prefix='institu'
        )
        form_investi = InvestigatorsForm(
            request.POST, prefix='investi'
        )
        if form.is_valid():
            data = form.save(commit=False)
            # we don't want to change ownership if someone else with
            # permission is updating the proposal
            if not proposal:
                data.user = user
            data.save()

            form_institu.is_valid()
            form_investi.is_valid()

            # delete the old objects because it's just easier this way
            if proposal:
                if investigators:
                    investigators.delete()
                if institutions:
                    institutions.delete()
            # obtain our new set of contacts
            institutions = form_institu.cleaned_data
            investigators = form_investi.cleaned_data
            for i in list(range(1,6)):
                institute = ProposalContact(
                    proposal=data,
                    institution=institutions['institution_{}'.format(i)]
                )
                institute.save()
                institute.tags.add('Other Institution')
                investigator = ProposalContact(
                    proposal=data,
                    name=investigators['name_{}'.format(i)],
                    institution=investigators['institution_{}'.format(i)],
                )
                investigator.save()
                investigator.tags.add('Co-Principal Investigators')

            # send emails only if we have a new proposal or a revised proposal
            if not proposal or data.opened:
                where = 'PT.pcn_03 = "{}"'.format(data.department)
                chairs = department_division_chairs(where)

                to_list = []
                # add approvers to distribution list
                for a in data.proposal_approvers.all():
                    to_list.append(a.user.email)

                if len(chairs) > 0:
                    # we need department full name in email
                    data.department_name = chairs[0][0]
                    # Division dean's email
                    to_list.append(chairs[0][8])
                    if DEBUG:
                        data.to_list = to_list
                        to_list = [MANAGER]
                else:
                    # staff do not have a dean so we send the email
                    # to OSP folks
                    to_list.append(PROPOSAL_EMAIL_LIST)
                    if DEBUG:
                        data.to_list = to_list
                        to_list = [MANAGER]

                    # for display purposes only in the email
                    data.department_name = depts[0][1]

                # if proposal has been reopened, we set opened to False
                # so that proposal now is considered a new attempt at approval
                data.opened = False
                data.save()

                # send the email to Dean or OSP
                subject = u'Review and Authorization Required for Part A: \
                    Your Approval Needed for "{}" by {}, {}'.format(
                    data.title, data.user.last_name, data.user.first_name
                )
                # OSP can update proposals after save/submit
                if not data.save_submit:
                    send_mail(
                        request, to_list, subject, PROPOSAL_EMAIL_LIST[0],
                        'proposal/email_approve.html', data, BCC
                    )
                # send confirmation to the Primary Investigator (PI)
                # who submitted the form
                subject = u"Part A Submission Received: {}".format(data.title)

                if DEBUG:
                    to_list = [MANAGER]
                    data.to_list = data.user.email
                else:
                    to_list = [data.user.email]

                # OSP can update proposals after save/submit
                if not data.save_submit:
                    send_mail(
                        request, to_list, subject, PROPOSAL_EMAIL_LIST[0],
                        'proposal/email_confirmation.html', data, BCC
                    )
                return HttpResponseRedirect(
                    reverse_lazy('proposal_success')
                )
            else:
                # set the data saved message
                # and redirect to proposal form
                messages.add_message(
                    request, messages.SUCCESS,
                    '''
                    Your proposal data have been saved.
                    ''',
                    extra_tags='success'
                )
                return HttpResponseRedirect(
                    reverse_lazy('proposal_update', kwargs={'pid':proposal.id})
                )
    else:
        form = ProposalForm(depts, instance=proposal)

        if proposal:
            investi = {}
            x = 1
            for i in investigators:
                investi['institution_'+ str(x)] = i.institution
                investi['name_'+ str(x)] = i.name
                x += 1
            institu = {}
            x = 1
            for i in institutions:
                institu['institution_'+ str(x)] = i.institution
                x += 1

        form_institu = InstitutionsForm(initial=institu, prefix='institu')
        form_investi = InvestigatorsForm(initial=investi, prefix='investi')
    return render(
        request, 'proposal/form.html', {
            'form': form, 'perms': perms,
            'form_institu': form_institu,
            'form_investi': form_investi
        }
    )


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied')
)
def proposal_detail(request, pid):
    '''
    Proposal detail view
    '''

    proposal = get_object_or_404(Proposal, id=pid)
    user = request.user

    # verify that the user can view this proposal
    # and if they are an approver or not
    perms = proposal.permissions(user)
    if not perms['view']:
        raise Http404

    co_principals = proposal.proposal_contact.filter(
        tags__name='Co-Principal Investigators'
    )
    institutions = proposal.proposal_contact.filter(
        tags__name='Other Institution'
    )

    return render(
        request, 'proposal/detail.html', {
            'proposal':proposal,'co_principals':co_principals,
            'institutions':institutions,'perms':perms
        }
    )


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied')
)
def proposal_approver(request, pid=0):
    '''
    Add an approver to a proposal.
    OJO: we still need to validate that a Dean  can add an approver
    to the proposal but we can trust deans for now.
    '''

    user = request.user
    group = in_group(user, OSP_GROUP, DEANS_GROUP)
    if not group:
        return HttpResponseRedirect(
            reverse_lazy('home')
        )
    else:
        proposal = None
        proposal = get_object_or_404(Proposal, id=pid)
        if request.method=='POST':
            form = ProposalApproverForm(request.POST, user=user)
            if form.is_valid():
                cd = form.cleaned_data
                cid = cd['user']
                try:
                    user = User.objects.get(id=cid)
                except:
                    # create a new user
                    l = LDAPManager()
                    luser = l.search(cid)
                    data = luser[0][1]
                    password = User.objects.make_random_password(length=24)
                    user = User.objects.create(
                        pk=cid, username=data['cn'][0],
                        email=data['mail'][0], last_login=NOW
                    )
                    user.set_password(password)
                    user.first_name = data['givenName'][0]
                    user.last_name = data['sn'][0]
                    user.save()

                approver = ProposalApprover(
                    user=user, proposal=proposal
                )

                where = 'PT.pcn_03 = "{}"'.format(proposal.department)
                chairs = department_division_chairs(where)
                # in the future, users might be able to select the role
                # that an approver might replace but for now we handle it
                # here and by default in the model, which is 'level3',
                # and if a dean is adding an approver there is no replace
                if len(chairs) > 0:
                    approver.replace = None
                approver.save()

                # send an email to approver
                prefix = 'Your Review and Authorization Required'
                subject = u'{}: "{}" by {}, {}'.format(
                    prefix, proposal.title,
                    proposal.user.last_name, proposal.user.first_name
                )

                if DEBUG:
                    to_list = [MANAGER]
                    proposal.to_list = [
                        proposal.user.email, approver.user.email
                    ]
                else:
                    to_list = [approver.user.email]
                    BCC = [MANAGER,]

                send_mail(
                    request, to_list, subject, PROPOSAL_EMAIL_LIST[0],
                    'approver/email.html', {'proposal':proposal,},BCC
                )

                return HttpResponseRedirect(
                    reverse_lazy('proposal_approver_success')
                )

        else:
            form = ProposalApproverForm(initial={'proposal': pid}, user=user)

    template = 'approver/form.html'
    context = {'proposal':proposal, 'form':form}

    return render(
        request, template, context
    )


@portal_auth_required(
    session_var='DJBECA_AUTH',
    redirect_url=reverse_lazy('access_denied')
)
def email_investigator(request, pid, action):
    '''
    send an email to the primary investigator
    '''

    form_data = None
    proposal = get_object_or_404(Proposal, id=pid)
    if request.method=='POST':
        form = EmailInvestigatorForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            if 'execute' in request.POST:
                if DEBUG:
                    to_list = [MANAGER]
                else:
                    to_list = [proposal.user.email]
                send_mail (
                    request, to_list,
                    u"[Office of Sponsored Programs] Grant Proposal: {}".format(
                        proposal.title
                    ),
                    request.user.email, 'investigator/email_data.html',
                    {'content':form_data['content']}, BCC
                )
                return HttpResponseRedirect(
                    reverse_lazy('email_investigator_done')
                )
            else:
                return render (
                    request, 'investigator/email_form.html',
                    {'form':form,'data':form_data,'p':proposal}
                )
    else:
        form = EmailInvestigatorForm()

    return render(
        request, 'investigator/email_form.html',
        {'form': form,'data':form_data,'p':proposal,'action':action}
    )


@csrf_exempt
@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied')
)
def proposal_status(request):
    '''
    scope:    set the status on a proposal.
    options:  approve, decline, open, close, needs work
    method:   AJAX POST
    '''

    # requires POST request
    if request.POST:
        pid = request.POST.get('pid')
        try:
            pid = int(pid)
        except:
            return HttpResponse("Access Denied")
        user = request.user
        approver = False
        proposal = get_object_or_404(Proposal, id=pid)
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
                    if proposal.impact():
                        proposal.proposal_impact.disclosure_assurance = False
                        proposal.proposal_impact.level3 = False
                        proposal.proposal_impact.level2 = False
                        proposal.proposal_impact.level1 = False
                        proposal.proposal_impact.save()
                    # Approvers
                    for a in proposal.proposal_approvers.all():
                        a.step1 = False
                        a.step2 = False
                        a.save()
                    return HttpResponse("Proposal has been closed")
                else:
                    return HttpResponse("You do not have permission to close")

            # open
            if status == 'open':
                if perms['open']:
                    # Approvers
                    for a in proposal.proposal_approvers.all():
                        if not proposal.step1() and not proposal.closed:
                            a.step1 = False
                        if proposal.step1() and not proposal.closed:
                            a.step2 = False
                        a.save()
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
                    if proposal.step1() and proposal.impact():
                        proposal.proposal_impact.disclosure_assurance = False
                        proposal.proposal_impact.level3 = False
                        proposal.proposal_impact.level2 = False
                        proposal.proposal_impact.level1 = False
                        proposal.proposal_impact.save()

                    return HttpResponse("Proposal has been reopened")
                else:
                    return HttpResponse("You do not have permission to open")

            # find out on which step we are
            decline_template = 'impact/email_decline.html'
            decline_subject = u'Part B: Not approved, requires \
                additional clarrification: "{}"'.format(proposal.title)
            needs_work_template = 'impact/email_needswork.html'
            needs_work_subject = u'Part B: Needs work, requires \
                additional clarrification: "{}"'.format(proposal.title)
            if not proposal.step1():
                step = 'step1'
                decline_template = 'proposal/email_decline.html'
                decline_subject = u'Part A: Not approved, requires \
                    additonal clarrification: "{}"'.format(proposal.title)
                needs_work_template = 'proposal/email_needswork.html'
                needs_work_subject = u'Part A: Needs work, requires \
                    additonal clarrification: "{}"'.format(proposal.title)
            elif proposal.step1() and not proposal.impact():
                return HttpResponse("Step 2 has not been initiated")
            elif proposal.impact() and not proposal.save_submit:
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
                        proposal.proposal_impact.level1 = False
                        proposal.proposal_impact.level2 = False
                        proposal.proposal_impact.level3 = False
                        proposal.proposal_impact.disclosure_assurance = False
                        proposal.proposal_impact.save()
                    # Approvers
                    for a in proposal.proposal_approvers.all():
                        if a.user == user:
                            if step == 'step1':
                                a.step1 = False
                            else:
                                a.step2 = False
                            a.save()
                            break
                    # send email to PI
                    to_list = [proposal.user.email]
                    if DEBUG:
                        proposal.to_list = to_list
                        to_list = [MANAGER]
                    send_mail(
                        request, to_list, decline_subject,
                        user.email, decline_template, proposal, BCC
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
                        proposal.proposal_impact.level1 = False
                        proposal.proposal_impact.level2 = False
                        proposal.proposal_impact.level3 = False
                        proposal.proposal_impact.disclosure_assurance = False
                        proposal.proposal_impact.save()
                    # Approvers
                    for a in proposal.proposal_approvers.all():
                        if step == 'step1':
                            a.step1 = False
                        else:
                            a.step2 = False
                        a.save()
                        break

                    to_list = [proposal.user.email]
                    if DEBUG:
                        proposal.to_list = to_list
                        to_list = [MANAGER]
                    send_mail(
                        request, to_list, needs_work_subject,
                        user.email, needs_work_template, proposal, BCC
                    )
                    return HttpResponse('Proposal "needs work" email sent')
                else:
                    return HttpResponse("Permission denied")

            #
            # begin approve logic
            #

            # default email subject
            subject = u'{}: "{}"'.format(
                'You are Approved to begin Part B', proposal.title
            )

            # establish the email distribution list
            to_list = [proposal.user.email]
            if DEBUG:
                proposal.to_list = to_list
                to_list = [MANAGER]

            # default message for when none of the conditions below are met
            message = "You do not have permission to '{}'".format(status)

            # if step1 and Division Dean
            if step == 'step1' and perms['level3']:
                proposal.level3 = True
                proposal.save()
                # send email to PI informing them that they are approved
                # to begin Part B
                send_mail(
                    request, to_list, subject, proposal.user.email,
                    'proposal/email_authorized.html', proposal, BCC
                )
                message = "Dean approved Part A"
            # if step2 and Division Dean
            elif step == 'step2' and perms['level3']:
                proposal.proposal_impact.level3 = True
                proposal.proposal_impact.save()
                message = "Division Dean approved Part B"
                # send email to Provost and VP for Business informing
                # them that the Division Dean has approved Part B
                # and the proposal is awaiting their approval.
                if proposal.ready_level1():
                    to_list = [VEEP.email, PROVOST.email]
                    if DEBUG:
                        proposal.to_list = to_list
                        to_list = [MANAGER]
                    subject = u'Review and Provide Final Authorization for PART B: "{}" by {}, {}'.format(
                        proposal.title, proposal.user.last_name, proposal.user.first_name
                    )

                    send_mail(
                        request, to_list, subject, PROPOSAL_EMAIL_LIST[0],
                        'impact/email_approve_level1.html', proposal, BCC
                    )
            # VP for Business?
            elif user.id == VEEP.id and step == 'step2':
                proposal.proposal_impact.level2 = True
                proposal.proposal_impact.save()
                message = "VP for Business approved Part B"
            # Provost?
            elif user.id == PROVOST.id and step == 'step2':
                proposal.proposal_impact.level1 = True
                proposal.proposal_impact.save()
                message = "Provost approved Part B"
            # approvers
            else:
                try:
                    a = proposal.proposal_approvers.get(user=user)
                    a.__dict__[step] = True
                    a.save()
                    # if approver replaces Division Dean set level3 to True
                    if a.replace == 'level3':
                        if step == 'step1':
                            proposal.level3 = True
                            proposal.save()
                        else:
                            proposal.proposal_impact.level3 = True
                            proposal.proposal_impact.save()
                    # if step 1 is complete send email notification
                    if (proposal.step1() and step == 'step1'):
                        send_mail(
                            request, to_list, subject, proposal.user.email,
                            'proposal/email_authorized.html', proposal, BCC
                        )
                    # if step 2 is complete and we are ready for
                    # VP for Business and Provost to weight in, send email
                    if proposal.ready_level1():

                        to_list = [VEEP.email, PROVOST.email]
                        if DEBUG:
                            proposal.to_list = to_list
                            to_list = [MANAGER]
                        subject = (
                            u'Review and Provide Final Authorization for PART B: '
                            '"{}" by {}, {}'
                        ).format(
                            proposal.title, proposal.user.last_name,
                            proposal.user.first_name
                        )

                        send_mail(
                            request, to_list, subject, PROPOSAL_EMAIL_LIST[0],
                            'impact/email_approve_level1.html', proposal, BCC
                        )

                    message = u"Approved by {} {}".format(
                        a.user.first_name, a.user.last_name
                    )
                except:
                    message = "You cannot change the status for this proposal"
    else:
        message = "Requires POST request"

    return HttpResponse(message)

