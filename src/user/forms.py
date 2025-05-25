from django import forms
from django.forms import Form, ModelForm
from common.django_utils import AsyncModelFormMixin
from django.utils.translation import gettext_lazy as _t

from typing import Iterable
from asgiref.sync import sync_to_async
from account.models import CustomUser

    
class UpdateUserForm(ModelForm, AsyncModelFormMixin):
    class Meta:
        model = CustomUser
        fields = {
            'email',
            'first_name',
            'last_name'
        }
#:

