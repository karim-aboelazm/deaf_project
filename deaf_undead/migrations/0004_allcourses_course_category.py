# Generated by Django 4.2 on 2023-05-10 21:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("deaf_undead", "0003_allcourses_coursescategories"),
    ]

    operations = [
        migrations.AddField(
            model_name="allcourses",
            name="course_category",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="deaf_undead.coursescategories",
            ),
            preserve_default=False,
        ),
    ]