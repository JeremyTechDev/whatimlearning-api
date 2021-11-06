# Generated by Django 3.2.9 on 2021-11-06 19:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('technologies', '0003_auto_20211106_0107'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='featuredcode',
            name='technology',
        ),
        migrations.AddField(
            model_name='technology',
            name='featured_code',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, to='technologies.featuredcode'),
            preserve_default=False,
        ),
    ]
