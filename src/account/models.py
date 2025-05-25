from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _t

from .managers import CustomUserManager


FIRST_NAME_MAX_LENGTH = 100
LAST_NAME_MAX_LENGTH = 160


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique= True, verbose_name="email_address")
    first_name = models.CharField(max_length=FIRST_NAME_MAX_LENGTH)
    last_name = models.CharField(max_length=LAST_NAME_MAX_LENGTH)
    is_active = models.BooleanField(default= True)
    is_staff = models.BooleanField(default= False)
    date_joined = models.DateTimeField(default=timezone.now)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    
    objects = CustomUserManager()
    
    def __str__(self) -> str:
        return self.email
    #:
#:
