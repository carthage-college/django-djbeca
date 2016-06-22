from django.apps import AppConfig


class ProposalConfig(AppConfig):
    name = 'djbeca.core'
    verbose_name = 'Proposal Application'
 
    def ready(self):
        import djbeca.core.signals
