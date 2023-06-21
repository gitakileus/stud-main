from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db import IntegrityError
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from knox.models import AuthToken
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import UserProfile

from .serializers import (ChangePasswordSerializer, CreateUserSerializer, CustomerSerializer,
                          LoginUserSerializer, UserSerializer)


class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        if str(request.data.get("authentication_type")) == str(UserProfile.SOCIAL):
            password = get_user_model().objects.make_random_password()
            request.data["password"] = password
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = serializer.save()
            try:
                UserProfile.objects.create(
                    user=request.user, user_role=request.data['user_role'],
                    country=request.data['country'], authentication_type=request.data['authentication_type'],
                    authentication_label=request.data['authentication_label'])
            except Exception as e:
                print("User profile is not created for requested user")
                pass

            subject = 'Activate Your Account'
            AuthToken.objects.create(user)

            email_verification_url = '%s/api/auth/email_verification?uid=%s&token=%s' % (
                request.build_absolute_uri('/')[:-1],
                urlsafe_base64_encode(force_bytes(user.pk)),
                list(AuthToken.objects.filter(user_id=user.pk).values_list(
                    'token_key', flat=True))[0],
            )

            try:
                message = render_to_string('email_verification.html', {
                    'username': user.first_name,
                    'email_verification_url': email_verification_url
                })
                email = EmailMessage(subject, message, to=[user.email])
                email.send()
            except Exception:
                pass

            return Response({
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "token": AuthToken.objects.create(user)[1]
            })
        except IntegrityError as e:
            return Response({
                'message': 'This user already exists.',
                'errors': {'Email or Username already exists.'}
            }, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data
            # set_password also hashes the password that the user will get
            user.set_password(request.data.get("new_password"))
            user.save()
            response = {
                'message': 'Password updated successfully',
            }
            return Response(data=response, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        if str(request.data.get("authentication_type")) == str(UserProfile.SOCIAL):
            UserModel = get_user_model()
            username = request.data.get("username")
            user = UserModel._default_manager.get_by_natural_key(username)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class UserAPI(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = CustomerSerializer

    def get_object(self):
        return self.request.user
