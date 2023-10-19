# Generated by Django 4.2.1 on 2023-10-17 09:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0009_message_recipient_checked_idx'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='found',
            name='coords',
        ),
        migrations.RemoveField(
            model_name='lost',
            name='coords',
        ),
        migrations.AddField(
            model_name='found',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, default=1, max_digits=9, verbose_name='Широта'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='found',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, default=1, max_digits=9, verbose_name='Долгота'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lost',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, default=1, max_digits=9, verbose_name='Широта'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lost',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, default=1, max_digits=9, verbose_name='Долгота'),
            preserve_default=False,
        ),
    ]
