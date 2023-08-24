# Generated by Django 4.2.1 on 2023-08-15 19:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ads', '0004_alter_animaltype_id_alter_found_id_alter_lost_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(verbose_name='Содержимое сообщения')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('checked', models.BooleanField(default=False, verbose_name='Просмотрено?')),
                ('advertisement_found', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ads.found')),
                ('advertisement_lost', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ads.lost')),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to=settings.AUTH_USER_MODEL, verbose_name='Получатель')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='send_messages', to=settings.AUTH_USER_MODEL, verbose_name='Отправитель')),
            ],
        ),
    ]