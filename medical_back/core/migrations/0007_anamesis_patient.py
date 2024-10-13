# Generated by Django 4.2.9 on 2024-09-10 14:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_images_anamesis'),
    ]

    operations = [
        migrations.AddField(
            model_name='anamesis',
            name='patient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='anamesis', to='core.patient'),
        ),
    ]