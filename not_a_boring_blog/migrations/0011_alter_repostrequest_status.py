# Generated by Django 4.2.4 on 2023-09-15 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('not_a_boring_blog', '0010_alter_post_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='repostrequest',
            name='status',
            field=models.CharField(choices=[('requested', 'Requested'), ('approved', 'Approved'), ('denied', 'Denied')], max_length=9),
        ),
    ]