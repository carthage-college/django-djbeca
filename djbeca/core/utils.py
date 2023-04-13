# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models import Q
from djbeca.core.models import Proposal
from djimix.people.departments import chair_departments
from djtools.utils.users import in_group
from djtools.utils.workday import get_deans


def deans_chairs(cid=False):
    """Obtain all deans or a dean."""
    deans = []
    response = requests.get(
        '{0}profile/deans/?format=json'.format(
            settings.DIRECTORY_API_URL,
        ),
        headers=HEADERS,
    )
    if response.json():
        for dean in response.json():
            if cid and cid == dean['id']:
                return response.json()
            else:
                deans.append(dean)
    return deans


def get_proposals(user):
    """Return all proposals for a user."""
    depts = False
    depts_props = False
    div = False
    dc = None
    dean = get_deans(user.id)
    # obtain user proposals and those where the user is an adhoc approver
    proposals = Proposal.objects.filter(
        Q(user=user) | Q(approvers__user=user),
    )

    group = in_group(user, settings.OSP_GROUP)
    if group:
        proposals = Proposal.objects.all()
    elif dean:
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
        'dean': dean,
        'dc': dc,
        'div': div,
        'depts': depts,
    }
