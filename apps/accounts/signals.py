from django.contrib.auth import get_user_model
from django.db.models.signals import post_save

from .models import UserProfile
from .services import apply_assignment_rules, sync_user_groups_from_profile

User = get_user_model()


def ensure_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, _ = UserProfile.objects.get_or_create(user=instance)
        sync_user_groups_from_profile(instance)
        apply_assignment_rules(instance)


def on_user_profile_saved(sender, instance, **kwargs):
    sync_user_groups_from_profile(instance.user)
    apply_assignment_rules(instance.user)


def connect_signals():
    post_save.connect(ensure_user_profile, sender=User, dispatch_uid='accounts_ensure_user_profile')
    post_save.connect(on_user_profile_saved, sender=UserProfile, dispatch_uid='accounts_apply_assignment_rules')
