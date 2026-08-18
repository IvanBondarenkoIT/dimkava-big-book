from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0008_course_description_en_course_description_ka_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprogress',
            name='quiz_answers',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
