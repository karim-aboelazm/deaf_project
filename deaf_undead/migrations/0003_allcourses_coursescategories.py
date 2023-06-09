# Generated by Django 4.2 on 2023-05-10 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("deaf_undead", "0002_newuser_user_type_friendship"),
    ]

    operations = [
        migrations.CreateModel(
            name="AllCourses",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("course_name", models.CharField(max_length=150)),
                ("course_poster", models.URLField()),
                ("course_description", models.TextField()),
                ("course_link", models.URLField()),
            ],
            options={
                "verbose_name_plural": "All Courses",
            },
        ),
        migrations.CreateModel(
            name="CoursesCategories",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
            ],
            options={
                "verbose_name_plural": "Courses Categories",
            },
        ),
    ]
