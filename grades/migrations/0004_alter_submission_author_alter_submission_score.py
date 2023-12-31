# Generated by Django 4.2.4 on 2023-10-21 05:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('grades', '0003_alter_submission_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='submission',
            name='score',
            field=models.FloatField(blank=True, default=None, null=True),
        ),
    ]
