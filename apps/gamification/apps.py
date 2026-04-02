from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GamificationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gamification'
    label = 'gamification'
    verbose_name = _('Gamification')

    def ready(self):
        from django.contrib.auth import get_user_model
        from django.db.models.signals import post_save

        from . import signals  # noqa: F401
        from .services import get_or_create_profile

        def ensure_profile(sender, instance, created, **kwargs):
            if created:
                get_or_create_profile(instance)

        post_save.connect(ensure_profile, sender=get_user_model(), dispatch_uid='gamification_ensure_profile')
