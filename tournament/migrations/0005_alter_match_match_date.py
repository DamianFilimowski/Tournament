# Generated by Django 4.2.3 on 2023-08-01 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0004_match_scorers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='match_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
