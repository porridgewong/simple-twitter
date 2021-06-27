from django.contrib import admin
from newsfeeds.models import Newsfeed


@admin.register(Newsfeed)
class NewsfeedAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'tweet', 'created_at')
    date_hierarchy = 'created_at'
