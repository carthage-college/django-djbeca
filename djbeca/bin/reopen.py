# -*- coding: utf-8 -*-

import django


django.setup()

from djbeca.core.models import Proposal


proposal = Proposal.objects.get(pk=666)
proposal.closed = False
proposal.level3 = True
proposal.email_approved = True
proposal.save_submit = True
proposal.save()
proposal.impact.level1 = True
proposal.impact.level2 = True
proposal.impact.level3 = True
proposal.disclosure_assurance = True
proposal.impact.save()
for approver in proposal.approvers.all():
    if approver:
        approver.step1 = True
        approver.step2 = True
        approver.save()
