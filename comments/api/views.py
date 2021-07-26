from comments.api.serializers import (
    CommentSerializerForCreate,
    CommentSerializer,
)
from comments.models import Comment
from rest_framework import viewsets
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
)
from rest_framework.response import Response
from rest_framework import status


class CommentViewSet(viewsets.GenericViewSet):
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content')
        }

        serializer = CommentSerializerForCreate(data=data)

        if not serializer.is_valid():
            return Response({
                    'message': 'Please check input',
                    'errors': serializer.errors,
                }, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()

        return Response(
                CommentSerializer(comment).data,
                status=status.HTTP_201_CREATED
            )
