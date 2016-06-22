from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

from djbeca.core.models import Proposal
from djtools.utils.mail import send_mail


@receiver(pre_save, sender=Proposal)
def proposal_pre_save(sender, **kwargs):
    obj = kwargs['instance']
    if not obj.email_approved:
        if obj.department_approved and obj.division_approved:
            if settings.DEBUG:
                TO_LIST = [settings.ADMINS[0][1],]
            else:
                TO_LIST = [settings.PROPOSAL_EMAIL,]
            BCC = settings.MANAGERS
            if obj.funding:
                if not settings.DEBUG:
                    TO_LIST.append(obj.use.email)
                # send the email
            subject = "[OSP Proposal][Update] {}: {}, {}".format(
                obj.title, obj.user.last_name, obj.user.first_name
            )
            sent = send_mail(
                kwargs.get("request"), TO_LIST, subject, settings.SERVER_MAIL,
                "proposal/email.html", obj, BCC
            )
            if sent:
                obj.email_approved = True

