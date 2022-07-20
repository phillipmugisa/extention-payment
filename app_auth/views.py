from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import auth


class loginUserView(View):
    template_name = 'account/login.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        
        if user is not None:
            auth.login(request, user)
            return redirect(reverse('manager:dashboard'))

        return render(request, self.template_name)


def logout(request):
    auth.logout(request)
    return redirect(reverse('app_auth:login'))