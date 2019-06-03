from django.conf import settings
from django.db.models import Q
from django.core.cache import cache

from djbeca.core.models import Proposal

from djtools.utils.users import in_group

from djzbar.utils.informix import do_sql
from djzbar.utils.hr import chair_departments
from djzbar.utils.hr import department_division_chairs


def get_proposals(user):

    approver = False
    depts = False
    div = False
    dc = None
    dean_chair = department_division_chairs(
        '(DTID.id={} or DVID.id={})'.format(user.id, user.id)
    )
    group = in_group(user, settings.OSP_GROUP)
    if group:
        objects = Proposal.objects.all().order_by('-grant_deadline_date')
    elif dean_chair:
        chair_depts = chair_departments(user.id)
        dc = chair_depts[1]
        div = chair_depts[2]
        depts = chair_depts[0]['depts']
        objects = Proposal.objects.filter(
            department__in=[ key for key,val in depts.iteritems() ]
        ).order_by('-grant_deadline_date')
    else:
        objects = Proposal.objects.filter(
            Q(user=user) | Q(approvers__user=user)
        ).order_by(
            '-grant_deadline_date'
        )

    # check if user is an approver
    for p in objects:
        for a in p.approvers.all():
            if a.user == user:
                approver = True
                break

    return {
        'objects':objects, 'dean_chair':dean_chair, 'dc':dc, 'div':div,
        'depts':depts, 'approver':approver
    }
