# Generated by Django 4.1.3 on 2022-11-14 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('festivalapp', '0011_alter_festival_poster'),
    ]

    operations = [
        migrations.AlterField(
            model_name='festival',
            name='ticket_link',
            field=models.URLField(blank=True, max_length=1000),
        ),
    ]
