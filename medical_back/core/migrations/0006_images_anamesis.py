# Generated by Django 4.2.9 on 2024-09-09 08:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_procedure_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Images',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('thumbnail', models.ImageField(null=True, upload_to='file/images/')),
                ('procedure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='core.procedure')),
            ],
        ),
        migrations.CreateModel(
            name='Anamesis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='anamesis', to='core.doctor')),
            ],
        ),
    ]