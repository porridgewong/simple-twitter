from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from friendships.services import FriendshipService
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class FollowersSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='from_user')
    created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return FriendshipService.has_followed(
            from_user=self.context['request'].user,
            to_user=obj.from_user
        )


class FollowingsSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')
    created_at = serializers.DateTimeField()
    has_followed = serializers.SerializerMethodField()

    class Meta:
        model = Friendship
        fields = ('user', 'created_at', 'has_followed')

    def get_has_followed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        return FriendshipService.has_followed(
            from_user=self.context['request'].user,
            to_user=obj.to_user
        )


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
