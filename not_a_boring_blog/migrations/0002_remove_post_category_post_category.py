# Generated by Django 4.2.4 on 2023-09-01 08:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("not_a_boring_blog", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="post",
            name="category",
        ),
        migrations.AddField(
            model_name="post",
            name="category",
            field=models.ManyToManyField(to="not_a_boring_blog.category"),
        ),
    ]
