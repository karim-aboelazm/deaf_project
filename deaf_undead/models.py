from django.db import models
from django.contrib.auth.models import User

class NewUser(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    profile = models.ImageField(upload_to='users/image/')
    user_type = models.CharField(max_length=30,choices=((i,i) for i in ["Deaf","Undeaf"]),blank=True)
    favorite_courses = models.ManyToManyField('AllCourses')
    class Meta:
        verbose_name_plural = 'New User'
    def __str__(self):
        return self.first_name+" "+self.last_name

class FriendShip(models.Model):
    STATUS=((i,i) for i in ['pending','accepted','declined'])
    from_user   = models.ForeignKey(NewUser, on_delete=models.CASCADE,related_name="friendship_sender")
    to_user     = models.ForeignKey(NewUser, on_delete=models.CASCADE,related_name="friendship_receiver")
    status      = models.CharField(max_length=10,choices=STATUS)
    class Meta:
        unique_together = ('from_user' , 'to_user')
    def __str__(self):
        return f"{self.from_user} - {self.to_user} ({self.status})"

class CoursesCategories(models.Model):
    name = models.CharField(max_length=50)
    class Meta:
        verbose_name_plural = 'Courses Categories'
    def __str__(self):
        return self.name
    
class AllCourses(models.Model):
    course_category     = models.ForeignKey(CoursesCategories, on_delete=models.CASCADE)
    course_name         = models.CharField(max_length=150)
    course_poster       = models.URLField()
    course_description  = models.TextField()
    course_link         = models.URLField()
    class Meta:
        verbose_name_plural = 'All Courses'
    def __str__(self):
        return self.course_name

class FavouritCourses(models.Model):
    user = models.ForeignKey(NewUser, on_delete=models.CASCADE)
    course = models.ForeignKey(CoursesCategories, on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = 'User Favourite Courses'
    def __str__(self):
        return self.course.name