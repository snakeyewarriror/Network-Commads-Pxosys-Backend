from rest_framework import serializers

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email as django_validate_email
from django.utils.translation import gettext_lazy as _t
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate

from .models import CustomUser



# Custom User Model Serializer
class CustomUserSerializer(serializers.ModelSerializer):
    
       
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
    )
    
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8,
    )
    
    
    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=160, required=True)
    
    class Meta:
        
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
        }
    #:
    
    
    def validate_email(self, value):
        # 1. Basic email format validation
        try:
            django_validate_email(value)
        #:
        
        except DjangoValidationError:
            raise serializers.ValidationError(_t("Enter a valid email address."))
        #:

        # 2. Check for email uniqueness
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError(_t("A user with that email already exists."))
        #:
        
        return value
    #:
    
    def validate(self, data):
        
        password = data.get('password')
        
        # password strength validation using Django's validators
        try:
            temp_user = CustomUser(email=data.get('email'))
            
            validate_password(data['password'], user=temp_user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        
        
        password2 = data.get('password2')
        email = data.get('email')


        # Ensure passwords exist for comparison
        if not password or not password2:
            raise serializers.ValidationError(_t("Both password fields are required."))


        # Check if password and password2 match
        if password != password2:
            raise serializers.ValidationError({"password2": _t("Password fields didn't match.")})
        #:


        try:
            temp_user = CustomUser(email=email)
            validate_password(password, user=temp_user)
        #:
            
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        #:

        return data
    #:

    
        
    def create(self, validated_data):
        # Remove 'password2' from validated_data as it's not a model field
        validated_data.pop('password2')

        # Extract 'password' to pass it directly to create_user for hashing
        password = validated_data.pop('password')

        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user
    #:
#:

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            # Check if user exists first (without revealing if password is correct yet)
            from django.contrib.auth import get_user_model
            CustomUser = get_user_model() # Use get_user_model() for custom user

            if not CustomUser.objects.filter(email=email).exists():
                # If email doesn't exist, return a specific error
                raise serializers.ValidationError(
                    {"email": "No account found with this email address."}
                )
            #:

            # If email exists, try to authenticate
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            if not user:
                # If authentication fails (wrong password or inactive user)
                raise serializers.ValidationError(
                    {"password": "Incorrect password for this email address."}
                )
            #:
            
            # If authentication succeeds, proceed with original validation
            data = super().validate(attrs)
            return data
        #:

        else:
            # If email or password is not provided (should be caught by required=True in serializer fields)
            raise serializers.ValidationError("Must include 'email' and 'password'.")
        #:
    #:
#:

