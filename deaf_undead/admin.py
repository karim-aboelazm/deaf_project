from django.contrib import admin
from .models import *

our_models = [NewUser,FriendShip,CoursesCategories,AllCourses,FavouritCourses]

for mod in our_models:
    admin.site.register(mod)