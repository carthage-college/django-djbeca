from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse_lazy

from djbeca.core.models import GenericContact, Proposal, ProposalApprover
from djbeca.core.forms import InstitutionsForm
from djbeca.core.forms import EmailInvestigatorForm
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

BCC = settings.MANAGERS


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
        proposals = Proposal.objects.all()
    elif dean_chair:
        chair_depts = chair_departments(user.id)
        dc = chair_depts[1]
        div = chair_depts[2]
        depts = chair_depts[0]['depts']
        proposals = Proposal.objects.filter(
            department__in=[ key for key,val in depts.iteritems() ]
        )
    else:
        proposals = Proposal.objects.filter(user=user)

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
def proposal_form(request, pid=None):
    TO_LIST = [settings.PROPOSAL_EMAIL,]

    institu = None
    investi = None
    proposal = None

    if pid:
        proposal = get_object_or_404(Proposal, id=pid)
        investigators = proposal.generic_contact.filter(
            tags__name='Co-Principal Investigators'
        )
        institutions = proposal.generic_contact.filter(
            tags__name='Other Institution'
        )
    depts = person_departments(request.user.id)
    if request.method=='POST':
        form = ProposalForm(
            depts, request.POST, request.FILES, instance=proposal
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
                institute = GenericContact(
                    proposal=data,
                    institution=institutions['institution_{}'.format(i)]
                )
                institute.save()
                institute.tags.add('Other Institution')
                investigator = GenericContact(
                    proposal=data,
                    name=investigators['name_{}'.format(i)],
                    institution=investigators['institution_{}'.format(i)],
                )
                investigator.save()
                investigator.tags.add('Co-Principal Investigators')

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
            subject = "[OSP Program Idea] {}, {}".format(
                data.user.last_name, data.user.first_name
            )
            send_mail(
                request, TO_LIST, subject, data.user.email,
                'proposal/email_approve.html', data, BCC
            )
            # send confirmation to individual submitting idea
            subject = "[OSP Program Idea] {}".format(
                data.title
            )
            send_mail(
                request, [data.user.email], subject, settings.PROPOSAL_EMAIL,
                'proposal/email_confirmation.html', data, BCC
            )
            '''

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
    co_principals = proposal.generic_contact.filter(
        tags__name='Co-Principal Investigators'
    )
    institutions = proposal.generic_contact.filter(
        tags__name='Other Institution'
    )
    if proposal.user != request.user and not group and not dean_chair:
        if not request.user.is_superuser:
            raise Http404

    return render(
        request, 'proposal/detail.html', {
            'proposal':proposal,'group':group,'co_principals':co_principals,
            'institutions':institutions
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
                data = form.cleaned_data
                cid = data['user']
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

                approver = ProposalApprover(user=user, proposal=proposal)
                approver.save()

                return HttpResponseRedirect(
                    reverse_lazy('proposal_approver_success')
                )
        else:
            form = ProposalApproverForm(initial={'proposal': pid})

    return render(
        request, 'approver/form.html', {
            'proposal':proposal, 'form':form
        }
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
                context = {'form':form,'data':form_data,'p':proposal}
                return render (
                    request, 'investigator/email_form.html', context
                )
            elif "execute" in request.POST:
                FEMAIL = request.user.email
                TO_LIST = [proposal.user.email,]
                data = {'content':form_data['content']}
                sub = "[Office of Sponsored Programs] Grant Proposal: {}".format(
                    proposal.title
                )
                send_mail (
                    request, TO_LIST, sub,
                    FEMAIL, 'investigator/email_data.html', data, BCC
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
