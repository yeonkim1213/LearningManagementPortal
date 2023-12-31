# Generated by Django 4.2.4 on 2023-10-21 04:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('grades', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='points',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='assignment',
            name='weight',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='submission',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='submission',
            name='file',
            field=models.FileField(upload_to='submissions/'),
        ),
    ]
