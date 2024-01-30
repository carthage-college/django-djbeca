# -*- coding: utf-8 -*-

from django.conf import settings
from django.db.models import Q
from djbeca.core.models import Proposal
from djtools.utils.users import in_group
from djtools.utils.workday import get_managers


def get_proposals(user):
    """Return all proposals for a user."""
    depts = False
    depts_props = False
    dean = get_managers('deans', cid=user.id)
    chair = get_managers('chairs', cid=user.id)
    # obtain user proposals and those where the user is an adhoc approver
    proposals = Proposal.objects.filter(
        Q(user=user) | Q(approvers__user=user),
    )
    group = in_group(user, settings.OSP_GROUP)
    depts = []
    if group:
        proposals = Proposal.objects.all()
    elif dean:
        for dept in dean[0]['managed']:
            depts.append(dept.split('/')[-2])
        depts_props = Proposal.objects.filter(department__in=depts)
        # merge them all together
        proposals = depts_props | proposals
    elif chair:
        did = chair['departments'][0].split('/')[-2]
        depts_props = Proposal.objects.filter(department=did)
        proposals = depts_props | proposals

    # finally order by
    if proposals:
        proposals = proposals.order_by('-grant_deadline_date')

    return {
        'objects': proposals,
        'dean': dean,
        'depts': depts,
    }
