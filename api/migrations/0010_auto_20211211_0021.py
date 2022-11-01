# Generated by Django 3.2.8 on 2021-12-10 21:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_post_favourite'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='favourite',
        ),
        migrations.CreateModel(
            name='FavouriteRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tguser')),
            ],
        ),
    ]
