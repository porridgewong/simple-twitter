"""twitter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from accounts.api import views as account_views
from comments.api import views as comment_views
from django.contrib import admin
from django.urls import include, path
from friendships.api import views as friendship_views
from inbox.api import views as notification_views
from likes.api import views as like_views
from newsfeeds.api import views as newsfeed_views
from rest_framework import routers
from tweets.api import views as tweet_views


router = routers.DefaultRouter()
router.register(r'api/users', account_views.UserViewSet)
router.register(r'api/accounts', account_views.AccountViewSet, basename='accounts')
router.register(r'api/tweets', tweet_views.TweetViewSet, basename='tweets')
router.register(r'api/friendships', friendship_views.FriendshipViewSet, basename='friendships')
router.register(r'api/newsfeeds', newsfeed_views.NewsfeedViewSet, basename='newsfeeds')
router.register(r'api/comments', comment_views.CommentViewSet, basename='comments')
router.register(r'api/likes', like_views.LikeViewSet, basename='likes')
router.register(r'api/notifications', notification_views.NotificationViewSet, basename='notifications')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]
