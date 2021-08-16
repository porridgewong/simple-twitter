from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.models import Comment
from comments.api.permissions import IsObjectOwner
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
    filterset_fields = ('tweet_id',)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    def list(self, request, *args, **kwargs):
        if 'tweet_id' not in request.query_params:
            return Response({
                'message': 'missing tweet_id in the request',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)

        comments = self.filter_queryset(self.get_queryset()).order_by('created_at')
        serializer = CommentSerializer(comments, context={'request': request}, many=True)
        return Response({
            'comments': serializer.data
        }, status=status.HTTP_200_OK)

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
                CommentSerializer(comment, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )

    def update(self, request, *args, **kwargs):
        serializer = CommentSerializerForUpdate(
            instance=self.get_object(),
            data=request.data
        )

        if not serializer.is_valid():
            return Response({
                    'message': 'Please check input'
                }, status=status.HTTP_400_BAD_REQUEST)

        comment = serializer.save()
        return Response(
                CommentSerializer(comment, context={'request': request}).data,
                status=status.HTTP_200_OK
            )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        return Response(
                {'success': True},
                status=status.HTTP_200_OK
            )
