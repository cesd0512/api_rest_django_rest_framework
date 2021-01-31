# Generated by Django 3.0.6 on 2021-01-18 00:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utsapi', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='download_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='consulted_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='favorite',
            field=models.BooleanField(default=False),
        ),
    ]