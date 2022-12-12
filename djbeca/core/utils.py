# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models import Q
from djbeca.core.models import Profile
from djbeca.core.models import Proposal
from djimix.people.departments import chair_departments
from djimix.people.departments import department_division_chairs
from djtools.utils.users import in_group
from sortedcontainers import SortedDict


def departments_all():
    """Returns department tuples for choices parameter in models and forms."""
    depts = (
        ('', '---Choose Your Department---'),
        ('', '---Faculty Departments---'),
    )
    profiles = Profile.objects.using('workday')
    faculty = profiles.filter(facstaff='faculty')
    staff = profiles.filter(facstaff='staff')
    for fac in faculty:
        depts.append((fac.department, fac.department))

    depts.append(('', '---Staff Deparments---'))

    for st in staff:
        depts.append((st.department, st.department))

    return depts


def get_proposals(user):
    """Return all proposals for a user."""
    depts = False
    depts_props = False
    div = False
    dc = None
    dean_chair = department_division_chairs(
        '(dept_id.id={0} OR div_id.id={1})'.format(user.id, user.id),
    )
    # obtain proposals where the user is an adhoc approver
    proposals = Proposal.objects.filter(
        Q(user=user) | Q(approvers__user=user),
    )

    group = in_group(user, settings.OSP_GROUP)
    if group:
        proposals = Proposal.objects.all()
    elif dean_chair:
        chair_depts = chair_departments(user.id)
        dc = chair_depts[1]
        div = chair_depts[2]
        depts = chair_depts[0]['depts']
        depts_props = Proposal.objects.filter(
            department__in=[key for key, _ in depts.items()],
        )
        # merge them all together
        proposals = depts_props | proposals

    # finally order by
    if proposals:
        proposals = proposals.order_by('-grant_deadline_date')

    return {
        'objects': proposals,
        'dean_chair': dean_chair,
        'dc': dc,
        'div': div,
        'depts': depts,
    }
