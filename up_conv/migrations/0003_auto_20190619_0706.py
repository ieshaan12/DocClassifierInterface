# Generated by Django 2.2.2 on 2019-06-19 07:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('up_conv', '0002_auto_20190618_0520'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='complaint_id',
            new_name='Application_ID',
        ),
    ]
