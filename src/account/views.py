from django.shortcuts import redirect
from django.http import HttpRequest, HttpResponse
import django.contrib.auth as auth
from common.django_utils import arender, alogout
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser
from .serializers import CustomUserSerializer
from common.auth import aanonymous_required


@aanonymous_required
async def home(request: HttpRequest) -> HttpResponse:
    return await arender(request, 'account/home.html')


@aanonymous_required
async def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if await form.ais_valid():
            await form.asave()
            return redirect('login')
        
        
    else:
        form = CustomUserCreationForm()
        
    
    context = {'register_form': form}
    return await arender(request, 'account/register.html', context)


@aanonymous_required
async def login(request: HttpRequest) -> HttpResponse:
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data = request.POST)
        if await form.ais_valid():
            email = request.POST['username']
            passwd = request.POST['password']
            user: CustomUser | None = await auth.aauthenticate(
                request,
                username = email,
                password = passwd,
            )
            
            if user:
                await auth.alogin(request, user)
                return redirect('commands' if user.is_staff else 'user-dashboard')
        
    else:
        form = CustomAuthenticationForm()
        
    
    context = {'login_form': form}
    return await arender(request, 'account/login.html', context)


@login_required(login_url='login')
async def logout(request: HttpRequest) -> HttpResponse:
    await alogout(request)
    return redirect('/')


class CreateUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]
#:

