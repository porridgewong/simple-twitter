from accounts.services import UserService
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveBigIntegerField()
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'),)
        index_together = (
            ('content_type', 'object_id', 'created_at'),
            ('user', 'content_type', 'created_at'),
        )

    @property
    def cached_user(self):
        return UserService.get_user_in_cache(self.user_id)

    def __str__(self):
        return u'{} - {} liked {} {}'.format(
            self.created_at, self.user, self.content_type, self.object_id)
