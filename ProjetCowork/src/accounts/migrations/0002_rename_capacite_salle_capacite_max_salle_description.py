# Generated by Django 5.1.7 on 2025-04-06 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salle',
            old_name='capacite',
            new_name='capacite_max',
        ),
        migrations.AddField(
            model_name='salle',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
