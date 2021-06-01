from accounts.api.serializers import UserSerializer, LoginSerializer
from django.contrib.auth import(
    logout as django_logout,
    login as django_login,
    authenticate as django_authenticate,
)
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class AccountViewSet(viewsets.ViewSet):
    @action(methods=['GET'], detail=False)
    def login_status(self, request):
        data = {'has_logged_in': request.user.is_authenticated}
        if request.user.is_authenticated:
            data['user'] = UserSerializer(request.user).data
        return Response(data)

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        django_logout(request)
        return Response({'success': True})

    @action(methods=['POST'], detail=False)
    def login(self, request):
        # User serializer to validate the input
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                    'success': False,
                    'message': 'Please check input',
                    'errors': serializer.errors
                },
                status=400)

        # Authenticate via django authenticate
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        if not User.objects.filter(username=username).exists():
            return Response({
                        'success': False,
                        'message': 'Please check input.',
                        'errors': {
                                'username': ['User does not exist.']
                            }
                    },
                    status=400)

        user = django_authenticate(username=username, password=password)
        if not user or user.is_anonymous:
            return Response({
                    'success': False,
                    'message': 'username and password do not match',
                },
                status=400)

        # login via django login
        django_login(request, user)
        return Response({
                'success': True,
                'user': UserSerializer(instance=user).data
            })
