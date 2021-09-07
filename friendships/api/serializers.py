from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from friendships.services import FriendshipService
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class FollowingUserIdSetMixin:
    @property
    def following_user_id_set(self: serializers.ModelSerializer):
        if self.context['request'].user.is_anonymous:
            return set()
        if hasattr(self, '_cached_following_user_id_set'):
            return self._cached_following_user_id_set

        user_id_set = FriendshipService.get_following_user_id_set(
            self.context['request'].user.id)

        setattr(self, '_cached_following_user_id_set', user_id_set)
        return user_id_set


class FollowersSerializer(
    serializers.ModelSerializer,
    FollowingUserIdSetMixin,
):
    user = UserSerializerForFriendship(source='cached_from_user')
    created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        return obj.from_user_id in self.following_user_id_set


class FollowingsSerializer(
    serializers.ModelSerializer,
    FollowingUserIdSetMixin,
):
    user = UserSerializerForFriendship(source='cached_to_user')
    created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        return obj.to_user_id in self.following_user_id_set


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user = serializers.IntegerField()
    to_user = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user', 'to_user')

    def validate(self, data):
        from_user = data['from_user']
        to_user = data['to_user']
        if from_user == to_user:
            raise ValidationError({'message': 'from_user id and to_user id should be different.'})

        if Friendship.objects.filter(from_user_id=from_user, to_user_id=to_user).exists():
            raise ValidationError({'message': 'The friendship has already existed.'})

        return data

    def create(self, validated_data):
        return Friendship.objects.create(
            from_user_id=validated_data['from_user'],
            to_user_id=validated_data['to_user'])
