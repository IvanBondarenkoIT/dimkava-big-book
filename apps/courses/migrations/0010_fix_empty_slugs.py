from django.db import migrations

TARGETS = [
    ('courses', 'Course', 'course'),
    ('knowledge_base', 'Article', 'article'),
    ('news', 'NewsPost', 'news'),
    ('onboarding', 'OnboardingProgram', 'program'),
]


def fix_empty_slugs(apps, schema_editor):
    for app_label, model_name, prefix in TARGETS:
        model = apps.get_model(app_label, model_name)
        for obj in model.objects.filter(slug=''):
            model.objects.filter(pk=obj.pk).update(slug=f'{prefix}_{obj.pk}')


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0009_userprogress_quiz_answers'),
        ('knowledge_base', '0003_article_content_en_article_content_ka_and_more'),
        ('news', '0002_newspost_content_en_newspost_content_ka_and_more'),
        ('onboarding', '0006_onboardingmodule_description_en_and_more'),
    ]

    operations = [
        migrations.RunPython(fix_empty_slugs, migrations.RunPython.noop),
    ]
