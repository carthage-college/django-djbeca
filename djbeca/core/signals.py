from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from djbeca.core.models import ProposalImpact
from djtools.utils.mail import send_mail


@receiver(post_save, sender=ProposalImpact)
def proposal_impact_poste_save(sender, **kwargs):
    obj = kwargs['instance'].proposal
    if not obj.decline and obj.step1() and obj.step2() \
      and not obj.email_approved:

        if settings.DEBUG:
            to_list = [settings.SERVER_EMAIL,]
        else:
            to_list = [settings.PROPOSAL_EMAIL,]

        # send the email
        subject = "Proposal approved {}: {}, {}".format(
            obj.title, obj.user.last_name, obj.user.first_name
        )
        sent = send_mail(
            kwargs.get('request'), to_list,
            subject, settings.SERVER_MAIL,
            'proposal/email_final_approved.html', obj, settings.MANAGERS
        )
        if sent:
            obj.email_approved = True
