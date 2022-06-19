# Generated by Django 4.0.2 on 2022-05-08 23:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('socialApp', '0002_alter_post_userpost'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ownerGroup', to='socialApp.profile'),
        ),
        migrations.AlterField(
            model_name='group',
            name='users',
            field=models.ManyToManyField(blank=True, null=True, related_name='usersGroup', to='socialApp.Profile'),
        ),
    ]
