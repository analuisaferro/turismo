# Generated by Django 3.2.10 on 2022-02-16 16:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contas', '0004_alter_cidade_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usuario',
            name='cadastur',
        ),
    ]
