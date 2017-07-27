from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse_lazy

from djbeca.core.choices import PROPOSAL_GOAL_CHOICES
from djbeca.core.models import Proposal, ProposalApprover, ProposalBudget
from djbeca.core.models import ProposalContact, ProposalGoal
from djbeca.core.forms import BudgetForm
from djbeca.core.forms import CommentsForm
from djbeca.core.forms import DocumentForm1, DocumentForm2, DocumentForm3
from djbeca.core.forms import EmailInvestigatorForm
from djbeca.core.forms import GoalsForm
from djbeca.core.forms import ImpactForm
from djbeca.core.forms import InstitutionsForm
from djbeca.core.forms import InvestigatorsForm
from djbeca.core.forms import ProposalForm
from djbeca.core.forms import ProposalApproverForm

from djzbar.utils.hr import chair_departments
from djzbar.utils.hr import person_departments
from djzbar.utils.hr import department_division_chairs
from djzbar.decorators.auth import portal_auth_required

from djtools.utils.mail import send_mail
from djtools.utils.users import in_group
from djtools.fields import NOW

from djauth.LDAPManager import LDAPManager

BCC = [settings.MANAGERS[0][1]]


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied')
)
def home(request):
    user = request.user
    group = in_group(user,'Sponsored Programs')
    depts = False
    div = False
    dc = None
    dean_chair = department_division_chairs(
        '(DTID.id={} or DVID.id={})'.format(user.id,user.id)
    )
    if group:
        proposals = Proposal.objects.all().order_by('-grant_deadline_date')
    elif dean_chair:
        chair_depts = chair_departments(user.id)
        dc = chair_depts[1]
        div = chair_depts[2]
        depts = chair_depts[0]['depts']
        proposals = Proposal.objects.filter(
            department__in=[ key for key,val in depts.iteritems() ]
        ).order_by('-grant_deadline_date')
    else:
        proposals = Proposal.objects.filter(user=user).order_by(
            '-grant_deadline_date'
        )

    return render(
        request, 'home.html',
        {
            'proposals':proposals,'dean_chair':dean_chair,
            'group':group,'dc':dc,'depts':depts,'div':div
        }
    )


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied')
)
def impact_form(request, pid):

    TO_LIST = [settings.PROPOSAL_EMAIL,]
    proposal = get_object_or_404(Proposal, id=pid)
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
            #if request.FILES.get('doc1-phile'):
            form_doc1.is_valid()
            doc1 = form_doc1.save(commit=False)
            doc1.proposal = proposal
            doc1.save()
            # document 2
            #if request.FILES.get('doc2-phile'):
            form_doc2.is_valid()
            doc2 = form_doc2.save(commit=False)
            doc2.proposal = proposal
            doc2.save()
            # document 3
            #if request.FILES.get('doc3-phile'):
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

            '''
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
            subject = "[OSP] Proposal: {} by {}, {}".format(
                data.title,
                data.user.last_name, data.user.first_name
            )
            send_mail(
                request, TO_LIST, subject, data.user.email,
                'proposal/email_approve.html', data, BCC
            )
            # send confirmation to individual submitting idea
            subject = "[OSP] Proposal: {}".format(
                data.title
            )
            send_mail(
                request, [data.user.email], subject, settings.PROPOSAL_EMAIL,
                'proposal/email_confirmation.html', data, BCC
            )
            '''

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
    institu = None
    investi = None
    proposal = None

    if pid:
        proposal = get_object_or_404(Proposal, id=pid)
        investigators = proposal.proposal_contact.filter(
            tags__name='Co-Principal Investigators'
        )
        institutions = proposal.proposal_contact.filter(
            tags__name='Other Institution'
        )
    depts = person_departments(request.user.id)
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
            data.user = request.user
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
            if not proposal:
                TO_LIST = []
                where = 'PT.pcn_03 = "{}"'.format(data.department)
                chairs = department_division_chairs(where)
                if len(chairs) > 0:
                    # temporarily assign department to full name
                    data.department = chairs[0][0]
                    if not settings.DEBUG:
                        # Division dean's email
                        TO_LIST.append(chairs[0][8])
                    else:
                        data.chairs = chairs
                else:
                    # staff do not have chairs
                    data.department = depts[0][1]

                if not TO_LIST:
                    TO_LIST = [settings.PROPOSAL_EMAIL,]
                else:
                    BCC.append(settings.PROPOSAL_EMAIL)

                # send the email
                subject = 'Grant Authorization Required: "{}" by {}, {}'.format(
                    data.title, data.user.last_name, data.user.first_name
                )
                send_mail(
                    request, TO_LIST, subject, data.user.email,
                    'proposal/email_approve.html', data, BCC
                )
                # send confirmation to the Primary Investigator (PI)
                # who submitted the form
                subject = "[OSP] Proposal: {}".format(
                    data.title
                )
                send_mail(
                    request, [data.user.email], subject,
                    settings.PROPOSAL_EMAIL,
                    'proposal/email_confirmation.html', data, BCC
                )

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

    proposal = get_object_or_404(Proposal, id=pid)
    user = request.user
    group = in_group(user,'Sponsored Programs')
    dean_chair = department_division_chairs(
        '(DTID.id={} or DVID.id={})'.format(user.id,user.id)
    )
    co_principals = proposal.proposal_contact.filter(
        tags__name='Co-Principal Investigators'
    )
    institutions = proposal.proposal_contact.filter(
        tags__name='Other Institution'
    )
    if proposal.user != request.user and not group and not dean_chair:
        if not request.user.is_superuser:
            raise Http404

    return render(
        request, 'proposal/detail.html', {
            'proposal':proposal,'group':group,'co_principals':co_principals,
            'institutions':institutions,'dean':dean_chair
        }
    )


@portal_auth_required(
    session_var='DJBECA_AUTH', redirect_url=reverse_lazy('access_denied')
)
def proposal_approver(request, pid=0):
    group = in_group(request.user,'Sponsored Programs')
    if not group:
        return HttpResponseRedirect(
            reverse_lazy('home')
        )
    else:
        proposal = None
        if pid:
            proposal = get_object_or_404(Proposal, id=pid)
        if request.method=='POST':
            form = ProposalApproverForm(request.POST)
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
                subject = '[OSP] Proposal: "{}" by {}, {}'.format(
                    proposal.title,
                    proposal.user.last_name, proposal.user.first_name
                )

                if settings.DEBUG:
                    TO_LIST = [settings.SERVER_EMAIL,]
                else:
                    TO_LIST = [proposal.user.email, approver.user.email]

                send_mail(
                    request, TO_LIST, subject, settings.PROPOSAL_EMAIL,
                    'approver/email.html', {'proposal':proposal,}, BCC
                )

                return HttpResponseRedirect(
                    reverse_lazy('proposal_approver_success')
                )

        else:
            form = ProposalApproverForm(initial={'proposal': pid})

    template = 'approver/form.html'
    #template = 'approver/email.html'
    context = {'proposal':proposal, 'form':form}
    #context = {'data': {'proposal':proposal}}

    return render(
        request, template, context
    )


@portal_auth_required(
    session_var='DJBECA_AUTH',
    group='Sponsored Programs',
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
            if 'confirm' in request.POST:
                return render (
                    request, 'investigator/email_form.html',
                    {'form':form,'data':form_data,'p':proposal}
                )
            elif "execute" in request.POST:
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
                return HttpResponseRedirect(
                    reverse_lazy('email_investigator_form', args=[pid,action])
                )
    else:
        form = EmailInvestigatorForm()

    return render(
        request, 'investigator/email_form.html',
        {'form': form,'data':form_data,"p":proposal,'action':action}
    )

'''
def approve_proposal(request, pid, step):
'''



