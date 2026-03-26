from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0006_feedback_models'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='userprogress',
            name='candidate_quiz_locked',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userprogress',
            name='candidate_retake_unlocked_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprogress',
            name='candidate_retake_unlocked_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='candidate_quiz_unlock_actions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='userprogress',
            name='quiz_attempts_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

