# Generated by Django 4.2.3 on 2023-08-01 21:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tournament', '0005_alter_match_match_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='Playoff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matches', models.ManyToManyField(to='tournament.match')),
                ('tournament', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='tournament.tournament')),
            ],
        ),
        migrations.CreateModel(
            name='GroupStage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('order', models.IntegerField()),
                ('matches', models.ManyToManyField(related_name='matches', to='tournament.match')),
                ('matches_finished', models.ManyToManyField(to='tournament.match')),
                ('promoted_teams', models.ManyToManyField(related_name='promoted_teams', to='tournament.team')),
                ('teams', models.ManyToManyField(to='tournament.team')),
                ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tournament.tournament')),
            ],
        ),
    ]