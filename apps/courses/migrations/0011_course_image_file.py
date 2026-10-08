from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_fix_empty_slugs'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='image_file',
            field=models.ImageField(blank=True, upload_to='courses/'),
        ),
    ]
