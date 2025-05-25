from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _t
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth import aget_user

from common.auth import auser_required, ensure_for_current_user
from common.django_utils import alogout, arender
from common.forms import CustomPasswordChangeForm
from .forms import UpdateUserForm

@auser_required
async def dashboard(resquest: HttpRequest) -> HttpResponse:
    
    user = await aget_user(resquest)
    
    context = {'is_staff': user.is_staff}
    return await arender(resquest, 'user/dashboard.html', context)
#:


@auser_required
async def update_user(request: HttpRequest) -> HttpResponse:
    user = await aget_user(request)
    subscription_plan = ''
    

    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=user)

        if await form.ais_valid():
            await form.asave()
            return redirect('user-dashboard')
    else:
        form = UpdateUserForm(instance=user)

    context = {
        'update_user_form': form,
    }

    return await arender(request, 'user/update-user.html', context)

   
@auser_required
async def password_update_user(request: HttpRequest) -> HttpResponse:
    user = await aget_user(request)
    
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user, request.POST)
        if await form.ais_valid():
            
            new_password1 = request.POST.get('new_password1')

            # Check if the old password is the same as the new one
            if check_password(new_password1, user.password):
                messages.warning(request, "Your new password must be different from your old password.")
            
            else:
                user = await form.asave()
                await alogout(request)
                return redirect('home')
        
        else:
            messages.error(request, "There was an error updating your password. Please correct the form errors.")

    else:
        form = CustomPasswordChangeForm(user)
    
    context = {
        'password_form': form,
    }
    return await arender(request, 'user/password-update.html', context)
#:


@auser_required
async def delete_account_user(request: HttpRequest) -> HttpResponse:
    user = await aget_user(request)
    
    if request.method == 'POST':
        await user.adelete()
        return redirect('home')
    
    context = {'user': user}
    return await arender(request, 'user/delete-account.html', context)
#:
  
