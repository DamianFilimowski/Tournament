# Generated by Django 4.2.3 on 2023-08-02 14:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0008_alter_match_team1_score_alter_match_team2_score'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='match',
            unique_together={('order', 'tournament', 'phase')},
        ),
    ]