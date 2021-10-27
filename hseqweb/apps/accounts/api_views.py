from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, logout
from accounts.models import UserProfile

from accounts.serializers import ChangePasswordSerializer, ReCaptchaSerializer, UserSerializer, UserShortSerializer
from hseqweb.apps.accounts.serializers import UserProfileSerializer

class Login(APIView):
    """ 
    loging
    """

    permission_classes = [AllowAny]
    def post(self, request, format='json'):
        username = request.data.get("username")
        password = request.data.get("password")

        serializer = ReCaptchaSerializer(data=request.data)
        if not serializer.is_valid():
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        if username is None or password is None:
            return Response({'error': 'Please provide both username and password'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Invalid username or password'},
                            status=status.HTTP_404_NOT_FOUND)
             
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, "username": user.username},status=status.HTTP_200_OK)

class VerifyTokenAPI(APIView):
    allowed_methods = ["POST"]

    def post(self, request, *args, **kwargs):
        serializer = ReCaptchaSerializer(data=request.data)
        if serializer.is_valid():
            return Response({'success': True}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateUser(APIView):
    """ 
    Creates the user. 
    """

    permission_classes = [AllowAny]
    def post(self, request, format='json'):
        serializer = ReCaptchaSerializer(data=request.data)
        if not serializer.is_valid():
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(UserShortSerializer(user).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetUser(APIView):
    """ 
    Get the user details. 
    """

    def get(self, request, format='json'):
        user = request.user
        return Response(UserShortSerializer(user).data, status=status.HTTP_200_OK)

class ChangePasswordView(APIView):
    """
    An endpoint for changing password.
    """
    model = User

    def put(self, request, format='json'):
        user = self.request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.data.get("old_password")):
                return Response({'error': 'old password is not correct'}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            user.set_password(serializer.data.get("new_password"))
            user.save()
            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileUpdateView(APIView):
    """
    An endpoint for update user profile
    """
    model = User

    def put(self, request, format='json'):
        user = self.request.user
        user.first_name=request.data['first_name']
        user.last_name=request.data['last_name']
        user.userprofile.organization=request.data['organization']
        user.userprofile.save()
        user.save()
        return Response(UserShortSerializer(user).data, status=status.HTTP_200_OK)

class UserLogoutView(APIView):

    def get(self, request, format='json'):
        request.user.auth_token.delete()
        logout(request)
        return Response(status=status.HTTP_200_OK)
