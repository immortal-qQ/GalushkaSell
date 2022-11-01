# Generated by Django 3.2.8 on 2021-10-16 09:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('header', models.CharField(max_length=64)),
                ('description', models.CharField(max_length=512)),
                ('image', models.ImageField(upload_to='static/post_images')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tguser')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.category')),
            ],
            options={
                'verbose_name': 'Post',
                'verbose_name_plural': 'Posts',
            },
        ),
    ]
