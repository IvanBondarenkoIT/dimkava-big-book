# Generated manually for email verification workflow.

from django.db import migrations, models
from django.utils import timezone


def set_existing_verified(apps, schema_editor):
    UserProfile = apps.get_model('accounts', 'UserProfile')
    now = timezone.now()
    UserProfile.objects.filter(email_verified_at__isnull=True).update(email_verified_at=now)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_candidate_profile_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='email_verified_at',
            field=models.DateTimeField(
                blank=True,
                help_text='Set when the user confirms their email (required for candidates before learning access).',
                null=True,
            ),
        ),
        migrations.RunPython(set_existing_verified, migrations.RunPython.noop),
    ]
