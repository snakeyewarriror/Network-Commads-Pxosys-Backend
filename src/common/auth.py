from functools import wraps

from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth import aget_user
from django.shortcuts import redirect

from account.models import CustomUser
from common.django_utils import AsyncViewT



__all__ = [
    'aclient_required',
    'astaff_required',
    'aanonymous_required',
    'aprofile_required',
    'ensure_for_current_user',
]


USER_PROFILES = {
    'user': lambda user: not user.is_staff,
    'staff': lambda user: user.is_staff,
}


def auser_required(user_view: AsyncViewT):
    
    @wraps(user_view)
    @login_required(login_url = 'login')
    async def function(resquest: HttpRequest, *args, **kwargs) -> HttpResponse:
        user = await aget_user(resquest)
        
        if user.is_authenticated and not user.is_staff:
            return await user_view(resquest, *args, **kwargs)
        
        return HttpResponseForbidden("Only logged in users can acess this view.")
    
    return function


def astaff_required(staff_view: AsyncViewT):
    @wraps(staff_view)
    @login_required(login_url = 'login')
    async def function(resquest: HttpRequest, *args, **kwargs) -> HttpResponse:
        user = await aget_user(resquest)
        
        if user.is_authenticated and user.staff:
            return await staff_view(resquest, *args, **kwargs)
        
        return HttpResponseForbidden("Only admnins can acess this view.")
    
    return function

def aprofile_required(profile: str, login_url: str = 'login'):
    
    if profile not in USER_PROFILES:
        raise ValueError(f"Unknown profile: {profile}")
    is_of_profile = USER_PROFILES[profile]
    
    def decorator(original_view: AsyncViewT):
        
        @login_required(login_url=login_url)
        @wraps(original_view)
        async def decorated_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            user: CustomUser = await aget_user(request)
            if user.is_authenticated and is_of_profile(user):
                return await original_view(request, *args, **kwargs)
            return HttpResponseForbidden(f"Only members of '{profile}' can access this page")
        return decorated_view
    
    return decorator


def aanonymous_required(original_view: AsyncViewT):
    @wraps(original_view)
    async  def decorated_view(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        user = await aget_user(request)
        redirect_to = (
            'user-dashboard' if user.is_authenticated
            else 'writer-dashboard' if user.is_authenticated and user.is_staff
            else ''
        )
        
        if redirect_to:
            return redirect(redirect_to)
        return await original_view(request, *args, **kwargs)
        
    return decorated_view


def ensure_for_current_user(model: type, *, id_in_url: str = 'id', redirect_if_missing: str):
    def decorator(view: AsyncViewT):
        async def async_view(request: HttpRequest, *args, **kargs) -> HttpResponse:
            obj_id = kargs[id_in_url]
            current_user = await aget_user(request)
            
            try:
                obj = await model.objects.aget(id = obj_id, user = current_user)
                del kargs[id_in_url]
                return await view(request, obj, *args, **kargs)
            except ObjectDoesNotExist:
                return redirect(redirect_if_missing)
            
        return async_view
    return decorator

