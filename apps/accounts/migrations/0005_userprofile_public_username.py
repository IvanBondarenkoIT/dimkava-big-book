from django.db import migrations, models
from django.utils.text import slugify


def backfill_public_username(apps, schema_editor):
    UserProfile = apps.get_model('accounts', 'UserProfile')
    for p in UserProfile.objects.select_related('user').all():
        if getattr(p, 'public_username', ''):
            continue
        email = getattr(p.user, 'email', '') or ''
        if email and '@' in email:
            base = email.split('@', 1)[0]
        else:
            base = getattr(p.user, 'username', '') or ''
        handle = (slugify(base) or 'user')[:40]
        p.public_username = handle
        p.save(update_fields=['public_username'])


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0004_userprofile_display_badge'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='public_username',
            field=models.SlugField(
                blank=True,
                db_index=True,
                help_text='Public handle shown in UI instead of email.',
                max_length=40,
            ),
        ),
        migrations.RunPython(backfill_public_username, migrations.RunPython.noop),
    ]

