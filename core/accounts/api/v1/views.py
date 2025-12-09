# project modules
from accounts.models import Profile
import decouple
from datetime import timedelta

from ..utils import EmailThread
from .serializers import (ActivationResendSerializer, ChangePasswordSerializer,
                          CustomAuthTokenSerializer,
                          CustomTokenObtainPairSerializer, PasswordResetConfirmSerializer,
                          PasswordResetRequestSerializer, ProfileSerializer,
                          RegistrationSerializer)

# rest framework
from rest_framework import generics, serializers
from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

# jwt
import jwt
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, InvalidSignatureError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

# django
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
# third party
from mail_templated import EmailMessage

User = get_user_model()


class RegistrationApiView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data["email"]
            data = {
                "email": email
            }
            user_obj = get_object_or_404(User, email=email)
            token = self.get_tokens_for_user(user_obj)
            email_obj = EmailMessage(
                "email/activation_email.tpl",
                {"token": token},
                "admin@admin.com",
                to=[email],
            )
            EmailThread(email_obj).start()
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            "user_id": user.pk,
            "email": user.email
        })


class CustomDiscardAuthToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        deleted_count, _ = Token.objects.filter(user=request.user).delete()
        if deleted_count == 0:
            return Response(
                {"detail": "Active token not found for this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ChangePasswordView(generics.GenericAPIView):
    model = User
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # check old password
            if not self.object.check_password(serializer.validated_data.get("old_password")):
                return Response({"old_password": ["wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set password also hashes the password that the user will get
            self.object.set_password(serializer.validated_data.get("new_password"))
            self.object.save()
            return Response({"details": "password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileApiView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self,):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj


class TestEmailSend(generics.GenericAPIView):
    """
    Sends the hello email template to either the authenticated user
    or the email provided through the `email` query parameter.
    """

    serializer_class = serializers.Serializer  # no request body, but DRF expects a serializer

    def get(self, request, *args, **kwargs):
        email = request.query_params.get("email")
        if not email and request.user.is_authenticated:
            email = request.user.email

        if not email:
            return Response(
                {"detail": "Provide an email query parameter or authenticate a user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_obj = get_object_or_404(User, email=email)
        token = self.get_tokens_for_user(user_obj)

        email_obj = EmailMessage(
            "email/hello.tpl",
            {"token": token},
            "admin@admin.com",
            to=[email],
        )
        EmailThread(email_obj).start()
        return Response("email sent")

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class ActivationApiView(APIView):
    def _generate_tokens(self, user):
        """Return both refresh and access tokens for the user."""
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def get(self, request, token, *args, **kwargs):
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"])
        except ExpiredSignatureError:
            return Response({"details": "token has been expired"}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidTokenError:
            return Response({"details": "token is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        except InvalidSignatureError:
            return Response({"details": "token signature is invalid"}, status=status.HTTP_400_BAD_REQUEST)

        user_id = payload.get("user_id")
        if not user_id:
            return Response({"details": "token payload missing user_id"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)
        already_verified = user.is_verified

        if not already_verified:
            user.is_verified = True
            user.save(update_fields=["is_verified"])

        tokens = self._generate_tokens(user)
        user_payload = {
            "id": user.id,
            "email": user.email,
            "is_verified": user.is_verified,
        }

        message = "user already verified" if already_verified else "user verified successfully"
        return Response(
            {
                "details": message,
                "user": user_payload,
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


class ActivationResendApiView(generics.GenericAPIView):
    serializer_class = ActivationResendSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data['user']
        token = self.get_tokens_for_user(user_obj)
        email_obj = EmailMessage(
            "email/hello.tpl", {"token": token}, "admin@admin.com", to=[user_obj.email],)
        EmailThread(email_obj).start()
        return Response({"details": "activation email resent"}, status=status.HTTP_200_OK)
        # else:
            # return Response({"details": "request failed"}, status=status.HTTP_400_BAD_REQUEST)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token = self._generate_reset_token(user)
        email_obj = EmailMessage(
            "email/reset_password_email.tpl",
            {"token": token},
            "admin@admin.com",
            to=[user.email],
        )
        EmailThread(email_obj).start()
        return Response({"details": "password reset email sent"}, status=status.HTTP_200_OK)

    def _generate_reset_token(self, user):
        token = AccessToken.for_user(user)
        token["token_use"] = "password_reset"
        token.set_exp(lifetime=timedelta(hours=1))
        return str(token)


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"details": "password reset successfully"}, status=status.HTTP_200_OK)
