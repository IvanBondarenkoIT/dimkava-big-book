from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('gamification', '0002_alter_badge_icon_charfield'),
        ('accounts', '0003_userprofile_email_verified_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='display_badge',
            field=models.ForeignKey(
                blank=True,
                help_text='Optional badge to display near the user avatar.',
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name='+',
                to='gamification.badge',
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='display_badge_placement',
            field=models.CharField(
                choices=[('corner', 'Corner'), ('overlay', 'Overlay')],
                default='corner',
                max_length=20,
            ),
        ),
    ]

