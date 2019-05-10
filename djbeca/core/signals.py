from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from djbeca.core.models import ProposalImpact
from djtools.utils.mail import send_mail

"""
If an approver has not approved the proposal before the
level1, level2, and level3 folks have done so, no email
is sent. we should create a new signal receiver for
ProposalApprover
"""

@receiver(post_save, sender=ProposalImpact)
def proposal_impact_post_save_notify_osp(sender, **kwargs):
    """
    send an email to the OSP when all approvals for a proposal
    have been met
    """

    obj = kwargs['instance'].proposal

    if not obj.decline and obj.step1() and obj.step2() \
    and not obj.email_approved:

        to_list = [settings.PROPOSAL_EMAIL_LIST,]
        if settings.DEBUG:
            obj.to_list = to_list
            to_list = [settings.MANAGERS[0][1],]

        # send the email OSP
        subject = "[Final] Proposal approved: '{}' by {}, {}".format(
            obj.title, obj.user.last_name, obj.user.first_name
        )
        sent = send_mail(
            kwargs.get('request'), to_list,
            subject, settings.SERVER_MAIL,
            'proposal/email_final_approved.html', obj, settings.MANAGERS
        )
        if sent:
            obj.email_approved = True
            obj.save()
