# Generated by Django 4.2.1 on 2023-10-20 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0010_remove_found_coords_remove_lost_coords_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='found',
            index=models.Index(fields=['active', 'open', 'latitude', 'longitude'], name='ads_found_active_3e61a8_idx'),
        ),
        migrations.AddIndex(
            model_name='lost',
            index=models.Index(fields=['active', 'open', 'latitude', 'longitude'], name='ads_lost_active_6f81a2_idx'),
        ),
    ]
