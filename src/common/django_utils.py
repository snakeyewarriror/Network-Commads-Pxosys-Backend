"""

Coomon django utils

"""



__all__ = (
    'AsyncFormMixin',
    'AsyncModelFormMixin',
    'AsyncViewT',
    'arender',
    'alogout',
)


from typing import Protocol

from django import forms
from asgiref.sync import sync_to_async
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

import django.contrib.auth as auth




class AsyncViewT(Protocol):
    """
    Type definition for an asynchronous view.
    """
    
    async def __call__(self, request: HttpRequest, *args, **kwds) -> HttpResponse:
        ...


class AsyncFormMixin():
    
    @sync_to_async
    def ais_valid(self: forms.BaseForm):
        return self.is_valid()
    
    @sync_to_async
    def arender(self: forms.BaseForm):
        return self.render()



class AsyncModelFormMixin(AsyncFormMixin):
    
    async def asave(self: forms.ModelForm, *args, **kargs):
        @sync_to_async
        def sync_call_save():
            return self.save(*args, **kargs)
        
        return await sync_call_save()


async def arender(*render_args, **render_kargs) -> HttpResponse:
    
    @sync_to_async
    def sync_call_render() -> HttpResponse:
        return render(*render_args, **render_kargs)
    
    return await sync_call_render()



async def alogout(*render_args, **render_kargs):
    @sync_to_async
    def sync_call_logout():
        auth.logout(*render_args, **render_kargs)
    await sync_call_logout()
