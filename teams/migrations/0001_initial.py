# Generated by Django 5.1.1 on 2024-09-10 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('characters', '0002_character_universe'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('universe', models.CharField(choices=[('Marvel', 'Marvel'), ('DC', 'DC')], max_length=10)),
                ('members', models.ManyToManyField(related_name='teams', to='characters.character')),
            ],
        ),
    ]
