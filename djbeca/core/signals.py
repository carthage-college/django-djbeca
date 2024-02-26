# -*- coding: utf-8 -*-

"""Signals for various events."""

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from djbeca.core.models import ProposalImpact
from djtools.utils.mail import send_mail


# If an approver has not approved the proposal before the
# level1, level2, and level3 folks have done so, no email
# is sent. we should create a new signal receiver for
# ProposalApprover


@receiver(post_save, sender=ProposalImpact)
def proposal_impact_post_save_notify_osp(sender, **kwargs):
    """Send an email to the OSP when all approvals have been met."""
    proposal = kwargs['instance'].proposal

    status = (
        not proposal.decline and
        proposal.step1() and
        proposal.step2() and
        not proposal.email_approved
    )
    if status:
        to_list = settings.PROPOSAL_EMAIL_LIST
        bcc [settings.MANAGERS[0][1]]
        if settings.DEBUG:
            proposal.to_list = to_list
            to_list = [settings.MANAGERS[0][1], settings.PROPOSAL_EMAIL_LIST[0]]
        # send the email OSP
        subject = "[Final] Proposal approved: '{0}' by {1}, {2}".format(
            proposal.title, proposal.user.last_name, proposal.user.first_name,
        )
        frum = settings.SERVER_MAIL
        sent = send_mail(
            kwargs.get('request'),
            recipients=to_list,
            subject=subject,
            femail=frum,
            template='proposal/email_final_approved.html',
            data=proposal,
            reply_to=settings.PROPOSAL_EMAIL_LIST[:1],
            bcc=bcc,
        )
        if sent:
            proposal.email_approved = True
            proposal.save()
