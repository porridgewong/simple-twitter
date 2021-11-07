from django_hbase import models


class HBaseFollowing(models.HBaseModel):
    # row key
    from_user_id = models.IntegerField(reverse=True)
    created_at = models.TimestampField()

    # column ky
    to_user_id = models.IntegerField(column_family='cf')

    class Meta:
        table_name = 'twitter_followings'
        row_key = ('from_user_id', 'created_at')


class HBaseFollower(models.HBaseModel):
    # row key
    to_user_id = models.IntegerField(reverse=True)
    created_at = models.TimestampField()

    # column ky
    from_user_id = models.IntegerField(column_family='cf')

    class Meta:
        table_name = 'twitter_followers'
        row_key = ('to_user_id', 'created_at')
