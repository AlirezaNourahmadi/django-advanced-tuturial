from rest_framework import serializers
from accounts.models import Profile
from ...models import User
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import TokenError


class RegistrationSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(max_length=250, write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "password1"]

    def validate(self, attrs):
        if attrs.get('password') != attrs.get("password1"):
            raise serializers.ValidationError(
                {"datails": "passwords does not match"})
        try:
            validate_password(attrs.get("password"))

        except exceptions.ValidationError as e:

            raise serializers.ValidationError({"password": list(e.messages)})

        return super().validate(attrs)

    def create(self, validated_data):
        validated_data.pop("password1", None)
        return User.objects.create_user(**validated_data)


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label=_("Email"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        username = attrs.get('email')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
            if not user.is_verified:
                raise serializers.ValidationError({"details":"user is not verified"})

        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):

        validated_data = super().validate(attrs)
        if not self.user.is_verified:
                raise serializers.ValidationError({"details":"user is not verified"})
        validated_data["email"] = self.user.email
        validated_data["user_id"] = self.user.id
        return validated_data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):

        if attrs.get('new_password') != attrs.get("new_password1"):
            raise serializers.ValidationError(
                {"datails": "passwords does not match"})
        try:
            validate_password(attrs.get("new_password"))

        except exceptions.ValidationError as e:

            raise serializers.ValidationError(
                {"new_password": list(e.messages)})

        return super().validate(attrs)


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ("id", "email", "first_name",
                    "last_name", "image", "description")
        read_only_fields = ["email",]

class ActivationResendSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    def validate(self, attrs):
        email = attrs.get("email")
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"details": "user with this email does not exist"})
        if user.is_verified:
            raise serializers.ValidationError(
                {"details": "user is already verified"})
        attrs['user'] = user
        return super().validate(attrs)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"details": "user with this email does not exist"}
            )

        if not user.is_active:
            raise serializers.ValidationError({"details": "user is inactive"})

        attrs["user"] = user
        return super().validate(attrs)


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)

    def validate(self, attrs):
        token = attrs.get("token")
        new_password = attrs.get("new_password")
        new_password1 = attrs.get("new_password1")

        if new_password != new_password1:
            raise serializers.ValidationError(
                {"details": "passwords does not match"}
            )

        try:
            validate_password(new_password)
        except exceptions.ValidationError as exc:
            raise serializers.ValidationError({"new_password": list(exc.messages)})

        try:
            untoken = UntypedToken(token)
        except TokenError:
            raise serializers.ValidationError({"token": "token is invalid or expired"})

        payload = untoken.payload
        if payload.get("token_use") != "password_reset":
            raise serializers.ValidationError({"token": "token type mismatch"})

        user_id = payload.get("user_id")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"token": "user not found"})

        attrs["user"] = user
        return super().validate(attrs)
