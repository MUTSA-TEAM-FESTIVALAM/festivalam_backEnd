# Generated by Django 4.1.3 on 2022-11-14 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('festivalapp', '0005_alter_festival_hits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='festival',
            name='hits',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
