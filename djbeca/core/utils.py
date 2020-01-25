# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models import Q
from djbeca.core.models import Proposal
from djimix.people.departments import chair_departments
from djimix.people.departments import department_division_chairs
from djtools.utils.users import in_group


def get_proposals(user):
    """Return all proposals for a user."""
    can_approve = False
    depts = False
    div = False
    dc = None
    dean_chair = department_division_chairs(
        '(DTID.id={0} or DVID.id={1})'.format(user.id, user.id)
    )
    group = in_group(user, settings.OSP_GROUP)
    if group:
        proposals = Proposal.objects.all().order_by('-grant_deadline_date')
    elif dean_chair:
        chair_depts = chair_departments(user.id)
        dc = chair_depts[1]
        div = chair_depts[2]
        depts = chair_depts[0]['depts']
        proposals = Proposal.objects.filter(
            department__in=[key for key, val in depts.items()]
        ).order_by('-grant_deadline_date')
    else:
        proposals = Proposal.objects.filter(
            Q(user=user) | Q(approvers__user=user)
        ).order_by('-grant_deadline_date')

    # check if user is an approver
    for proposal in proposals:
        for approver in proposal.approvers.all():
            if approver.user == user:
                can_approve = True
                break

    return {
        'objects': proposals,
        'dean_chair': dean_chair,
        'dc': dc,
        'div': div,
        'depts': depts,
        'approver': can_approve,
    }
