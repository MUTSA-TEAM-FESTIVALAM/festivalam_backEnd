from django.contrib import admin

# Register your models here.
from festivalapp.models import User, Post, Festival

admin.site.register(User)
admin.site.register(Post)
admin.site.register(Festival)