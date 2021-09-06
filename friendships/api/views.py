from django.contrib.auth.models import User
from friendships.api.paginations import FriendshipPagination
from friendships.api.serializers import (
    FollowersSerializer,
    FollowingsSerializer,
    FriendshipSerializerForCreate,
)
from friendships.models import Friendship
from friendships.services import FriendshipService
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework import status
from rest_framework.exceptions import ValidationError


class FriendshipViewSet(viewsets.GenericViewSet):
    serializer_class = FriendshipSerializerForCreate
    queryset = User.objects.all()
    pagination_class = FriendshipPagination

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followers(self, request, pk):
        friendships = Friendship.objects.filter(to_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowersSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['GET'], detail=True, permission_classes=[AllowAny])
    def followings(self, request, pk):
        friendships = Friendship.objects.filter(from_user_id=pk).order_by('-created_at')
        page = self.paginate_queryset(friendships)
        serializer = FollowingsSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def follow(self, request, pk):
        followed_user = self.get_object()
        serializer = FriendshipSerializerForCreate(
            data={
                'from_user': request.user.id,
                'to_user': followed_user.id
            })

        if not serializer.is_valid():
            return Response({
                    'success': False,
                    'message': 'please check input',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        FriendshipService.invalidate_following_cache(request.user.id)
        return Response({
                'success': True
            }, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk):
        unfollow_user = self.get_object()
        if request.user.id == unfollow_user.id:
            raise ValidationError({'message': 'you cannot unfollow yourself.'})

        delete, _ = Friendship.objects.filter(
                    from_user_id=request.user.id,
                    to_user_id=unfollow_user.id
                ).delete()
        FriendshipService.invalidate_following_cache(request.user.id)
        return Response({'success': True, 'deleted': delete}, status=status.HTTP_200_OK)
