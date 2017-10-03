from django.conf import settings
from django.shortcuts import render
from django.template import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, Http404

from djbeca.core.models import Proposal, ProposalApprover, ProposalBudget
from djbeca.core.models import ProposalContact, ProposalGoal
from djbeca.core.choices import PROPOSAL_GOAL_CHOICES
from djbeca.core.forms import *
from djbeca.core.utils import get_position, get_proposals

from djzbar.utils.hr import person_departments
from djzbar.utils.hr import department_division_chairs
from djzbar.decorators.auth import portal_auth_required

from djtools.utils.mail import send_mail
from djtools.utils.users import in_group
from djtools.fields import NOW

from djauth.LDAPManager import LDAPManager

BCC = [settings.MANAGERS[0][1],settings.PROPOSAL_EMAIL]
OSP_GROUP = settings.OSP_GROUP
DEANS_GROUP = settings.DEANS_GROUP
VEEP = get_position(settings.VEEP_TPOS)
PROVOST = get_position(settings.PROV_TPOS)
PRESIDENT = get_position(settings.PREZ_TPOS)
PROPOSAL_EMAIL = settings.PROPOSAL_EMAIL
SERVER_EMAIL = settings.SERVER_EMAIL
DEBUG = settings.DEBUG


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied')
)
def home(request):
    '''
    dashboard home page view
    '''

    user = request.user
    group = in_group(user, OSP_GROUP)
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


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied')
)
def impact_form(request, pid):
    '''
    Proposal Form Part B view
    '''

    proposal = get_object_or_404(Proposal, id=pid)

    # we do not allow PIs to update their proposals after save-submit
    # but OSP can do so
    group = in_group(request.user, OSP_GROUP)
    if not group and proposal.save_submit:
        return HttpResponseRedirect(
            reverse_lazy('home')
        )

    # budget and impact
    try:
        impact = proposal.proposal_impact
        budget = proposal.proposal_budget
    except:
        impact = budget = None
    # goals
    try:
        goals = proposal.proposal_goal.all()
    except:
        goals = None
    # documents
    docs = [None,None,None]
    for c, d in enumerate(proposal.proposal_documents.all()):
        docs[c] = d

    if request.method=='POST':
        form_impact = ImpactForm(
            request.POST, instance=impact, prefix='impact', label_suffix=''
        )
        form_budget = BudgetForm(
            request.POST, request.FILES,
            instance=budget, prefix='budget', label_suffix=''
        )
        form_comments = CommentsForm(
            request.POST, prefix='comments', label_suffix=''
        )
        form_goals = GoalsForm(
            request.POST, prefix='goal'
        )
        form_doc1 = DocumentForm1(
            request.POST, request.FILES,
            instance=docs[0], prefix='doc1', label_suffix=''
        )
        form_doc2 = DocumentForm1(
            request.POST, request.FILES,
            instance=docs[1], prefix='doc2', label_suffix=''
        )
        form_doc3 = DocumentForm1(
            request.POST, request.FILES,
            instance=docs[2], prefix='doc3', label_suffix=''
        )
        if form_impact.is_valid() and form_budget.is_valid():
            # proposal impact
            impact = form_impact.save(commit=False)
            impact.proposal = proposal
            impact.save()
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
            form_doc1.is_valid()
            doc1 = form_doc1.save(commit=False)
            doc1.proposal = proposal
            doc1.save()
            # document 2
            form_doc2.is_valid()
            doc2 = form_doc2.save(commit=False)
            doc2.proposal = proposal
            doc2.save()
            # document 3
            form_doc3.is_valid()
            doc3 = form_doc3.save(commit=False)
            doc3.proposal = proposal
            doc3.save()

            # delete the old goals because it's just easier this way
            if impact:
                if goals:
                    goals.delete()
            # obtain our new set of goals
            form_goals.is_valid()
            goals = form_goals.cleaned_data
            # create the new goals
            for i in list(range(1,8)):
                name = goals['name_{}'.format(i)]
                desc = goals['description_{}'.format(i)]
                if name and desc:
                    goal = ProposalGoal(
                        proposal=proposal, name=name, description=desc
                    )
                    goal.save()

            # Send email to Approvers, Division Dean, VEEP/CFO, and Provost
            # if the PI is finished with the proposal (i.e. hits 'submit-save'
            # rather than 'save and continue')
            post = request.POST
            if post.get('save_submit') and not proposal.save_submit:
                subject = 'Routing & Authorization Form Part B: Your Approval Needed for "{}" by {}, {}'.format(
                    proposal.title, proposal.user.last_name,
                    proposal.user.first_name
                )

                # Approvers
                to_list = []
                for a in proposal.proposal_approvers.all():
                    to_list.append(a.user.email)

                if to_list:
                    # send the email to Approvers
                    send_mail(
                        request, to_list, subject, proposal.user.email,
                        'impact/email_approve_approvers.html', proposal, BCC
                    )

                subject = 'Review and Provide Final Authorization for PART B: "{}" by {}, {}'.format(
                    proposal.title, proposal.user.last_name,
                    proposal.user.first_name
                )
                # Division Dean (level3)
                where = 'PT.pcn_03 = "{}"'.format(proposal.department)
                chairs = department_division_chairs(where)
                # staff do not have deans so len will be 0 in that case
                if len(chairs) > 0:
                    # we need department full name in email
                    proposal.department_name = chairs[0][0]
                    if DEBUG:
                        to_list = [SERVER_EMAIL]
                    else:
                        # Division dean's email
                        to_list = [chairs[0][8]]

                    # send the email
                    send_mail(
                        request, to_list, subject, proposal.user.email,
                        'impact/email_approve_level3.html', proposal, BCC
                    )

                # Veep/CFO (level2) and Provost (level1)
                send_mail(
                    request, [VEEP.email, PROVOST.email], subject,
                    PROPOSAL_EMAIL, 'impact/email_approve_level1.html',
                    proposal, BCC
                )

                # send confirmation to the Primary Investigator (PI)
                # who submitted the form
                subject = "[Part B] Submission Received: {}".format(
                    proposal.title
                )
                send_mail(
                    request, [proposal.user.email], subject, PROPOSAL_EMAIL,
                    'impact/email_confirmation.html', proposal, BCC
                )
                # set the save submit flag so PI cannot update
                proposal.save_submit = True
                proposal.save()
            # end sendmail

            return HttpResponseRedirect(
                reverse_lazy('impact_success')
            )
    else:
        form_impact = ImpactForm(
            instance=impact, prefix='impact', label_suffix=''
        )
        form_budget = BudgetForm(
            instance=budget, prefix='budget', label_suffix=''
        )
        form_comments = CommentsForm(
            initial={'comments':proposal.comments},
            prefix='comments', label_suffix=''
        )
        form_doc1 = DocumentForm1(
            instance=docs[0], prefix='doc1', label_suffix=''
        )
        form_doc2 = DocumentForm1(
            instance=docs[1], prefix='doc2', label_suffix=''
        )
        form_doc3 = DocumentForm1(
            instance=docs[2], prefix='doc3', label_suffix=''
        )

    return render(
        request, 'impact/form.html', {
            'form_budget': form_budget,
            'form_comments': form_comments,
            'form_impact': form_impact,
            'form_doc1': form_doc1,
            'form_doc2': form_doc2,
            'form_doc3': form_doc3,
            'goals': goals,
            'goal_choices':[p[1] for p in PROPOSAL_GOAL_CHOICES],
            'copies':len(goals)
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
    user = request.user

    if pid:
        proposal = get_object_or_404(Proposal, id=pid)
        investigators = proposal.proposal_contact.filter(
            tags__name='Co-Principal Investigators'
        )
        institutions = proposal.proposal_contact.filter(
            tags__name='Other Institution'
        )
        # we do not allow PIs to update their proposals after save-submit
        # but OSP can do so
        group = in_group(user, OSP_GROUP)
        if not group and proposal.save_submit:
            return HttpResponseRedirect(
                reverse_lazy('home')
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

            # send emails only if we have a new proposal
            if not proposal or proposal.opened:
                to_list = []
                where = 'PT.pcn_03 = "{}"'.format(data.department)
                chairs = department_division_chairs(where)
                if len(chairs) > 0:
                    # we need department full name in email
                    data.department_name = chairs[0][0]
                    if DEBUG:
                        data.chairs = chairs
                    else:
                        # Division dean's email
                        to_list.append(chairs[0][8])
                else:
                    # staff do not have a dean
                    data.department_name = depts[0][1]

                if not to_list:
                    if DEBUG:
                        to_list = [SERVER_EMAIL]
                        # we might not have chairs
                        try:
                            data.to_list = chairs[0][8]
                        except:
                            data.to_list = PROPOSAL_EMAIL
                    else:
                        to_list = [PROPOSAL_EMAIL]

                # send the email
                subject = 'Review and Authorization Required for Part A: \
                    Your Approval Needed for "{}" by {}, {}'.format(
                    data.title, data.user.last_name, data.user.first_name
                )
                send_mail(
                    request, to_list, subject, PROPOSAL_EMAIL,
                    'proposal/email_approve.html', data, BCC
                )
                # send confirmation to the Primary Investigator (PI)
                # who submitted the form
                subject = "Part A Submission Received: {}".format(data.title)

                if DEBUG:
                    to_list = [SERVER_EMAIL]
                    data.to_list = data.user.email
                else:
                    to_list = [data.user.email]

                send_mail(
                    request, to_list, subject, PROPOSAL_EMAIL,
                    'proposal/email_confirmation.html', data, BCC
                )

            # if proposal has been reopened, we set opened to False
            # so that proposal now is considered a new attempt at approval
            if proposal.opened:
                data.opened = False
                data.save()

            return HttpResponseRedirect(
                reverse_lazy('proposal_success')
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
            'form': form,
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
    Add an approver to a proposal
    '''

    user = request.user
    group = in_group(user, OSP_GROUP, DEANS_GROUP)
    if not group:
        return HttpResponseRedirect(
            reverse_lazy('home')
        )
    else:
        proposal = None
        if pid:
            proposal = get_object_or_404(Proposal, id=pid)
        if request.method=='POST':
            form = ProposalApproverForm(request.POST, user=user)
            if form.is_valid():
                # shouldn't return a 404 but just in case someone is doing
                # something untoward or nefarious
                cd = form.cleaned_data
                proposal = get_object_or_404(Proposal, id=cd['proposal'])
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
                approver.save()

                # send an email to approver
                prefix = 'Your Review and Authorization Required'
                subject = '{}: "{}" by {}, {}'.format(
                    prefix, proposal.title,
                    proposal.user.last_name, proposal.user.first_name
                )

                if DEBUG:
                    to_list = [SERVER_EMAIL]
                else:
                    to_list = [proposal.user.email, approver.user.email]

                send_mail(
                    request, to_list, subject, PROPOSAL_EMAIL,
                    'approver/email.html', {'proposal':proposal,}, BCC
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
                send_mail (
                    request, [proposal.user.email,],
                    "[Office of Sponsored Programs] Grant Proposal: {}".format(
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
    approve or decline a proposal via AJAX POST
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
        # regardless of whether we are approving, decling, or closing/opening
        if not perms['approve'] and not perms['open']:
            return HttpResponse("Access Denied")
        else:
            status = request.POST.get('status')
            if not status:
                return HttpResponse("No status")

            if status == 'close':
                if perms['close']:
                    proposal.closed = True
                    proposal.save()
                    return HttpResponse("Proposal has been closed")
                else:
                    return HttpResponse("You do not have permission to close")

            # simple open or close, not dependent on anything else (e.g. steps)
            if status == 'open':
                if perms['open']:
                    # reset all booleans back to False
                    proposal.closed = False
                    proposal.opened = True
                    proposal.decline = False
                    proposal.level3 = False
                    proposal.email_approved = False
                    proposal.save_submit = False
                    proposal.save()
                    # we might not have a proposal impact relationship
                    try:
                        proposal.proposal_impact.disclosure_assurance = False
                        proposal.proposal_impact.level3 = False
                        proposal.proposal_impact.level2 = False
                        proposal.proposal_impact.level1 = False
                        proposal.proposal_impact.save()
                    except:
                        pass
                    return HttpResponse("Proposal has been reopened")
                else:
                    return HttpResponse("You do not have permission to open")

            # find out on which step we are
            decline_template = 'impact/email_decline.html'
            decline_subject = 'Part B: Not approved, requires \
                additional clarrification: "{}"'.format(proposal.title)
            if not proposal.step1():
                step = 'step1'
                decline_template = 'proposal/email_decline.html'
                decline_subject = 'Part A: Not approved, requires \
                    additonal clarrification: "{}"'.format(proposal.title)
            elif proposal.step1() and not proposal.impact():
                return HttpResponse("Step 2 has not been initiated")
            elif proposal.proposal_impact and not proposal.step2():
                return HttpResponse("Step 2 has not been completed")
            else:
                step = 'step2'

            # we can stop here if declined.
            # anyone can decline, for now. i suspect that will change
            # and thus the data model will have to change.
            if status == 'decline':
                if perms['decline']:
                    proposal.decline = True
                    proposal.closed = True
                    proposal.save()
                    if DEBUG:
                        to_list = [SERVER_EMAIL]
                    else:
                        to_list = [proposal.user.email]
                    send_mail(
                        request, to_list, decline_subject,
                        proposal.user.email, decline_template, proposal, BCC
                    )
                    return HttpResponse("Proposal Declined")
                else:
                    return HttpResponse("You don't have permission to decline")


            # default email subject
            subject = '{}: "{}"'.format(
                'You are Approved to begin Part B:',
                proposal.title
            )

            # establish the email distribution list
            if DEBUG:
                to_list = [SERVER_EMAIL]
            else:
                to_list = [proposal.user.email]

            # if step1 and dean stop here
            if step == 'step1' and perms['level3']:
                proposal.level3 = True
                proposal.save()
                send_mail(
                    request, to_list, subject,
                    proposal.user.email, "proposal/email_authorized.html",
                    proposal, BCC
                )
                message = "Dean approved Part A"
            # Dean?
            elif perms['level3']:
                proposal.proposal_impact.level3 = True
                proposal.proposal_impact.save()
                message = "Division Dean approved Part B"
            # Veep/CFO?
            elif user.id == VEEP.id:
                proposal.proposal_impact.level2 = True
                proposal.proposal_impact.save()
                message = "VP for Businees approved Part B"
            # Provost?
            elif user.id == PROVOST.id:
                proposal.proposal_impact.level1 = True
                proposal.proposal_impact.save()
                message = "Provost approved Part B"
            else:
                # approvers
                for a in proposal.proposal_approvers.all():
                    if a.user == user:
                        a.__dict__[step] = True
                        a.save()
                        # right now, approvers only replace deans
                        if a.replace == 'level3':
                            proposal.level3 = True
                            proposal.save()
                            if step != 'step2':
                                send_mail(
                                    request, to_list, subject,
                                    proposal.user.email,
                                    "proposal/email_authorized.html",
                                    proposal, BCC
                                )
                        approver = True
                        break

            if approver:
                message = "Approved by {} {}".format(
                    a.user.first_name, a.user.last_name
                )
            else:
                message = "Who dat tryin' to 'prove?"
    else:
        message = "Requires POST request"

    return HttpResponse(message)

