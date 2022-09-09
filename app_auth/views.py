from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import auth
from app_auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import HttpResponse

from django.contrib import messages


def login_complete(request, source):
    if request.user.is_authenticated:
        refresh = RefreshToken.for_user(request.user)
        response = HttpResponse("", status=200)
        response.set_cookie('refresh', str(refresh))
        response.set_cookie('access', str(refresh.access_token))
        response.delete_cookie('user_type')
        return response

    return HttpResponse("", status=200) 

class loginUserView(View):
    template_name = "account/login.html"

    def get(self, request, *args, **kwargs):
        context_data = {
            'userType': kwargs.get('usertype', None)
        }
        response = render(request, self.template_name, context=context_data)

        if kwargs.get('usertype', None):
            response.set_cookie('user_type', "extension")

        if request.user.is_authenticated:
            response = redirect(reverse("manager:dashboard"))
            if kwargs.get('usertype', None):
                response.set_cookie('user_type', "extension")
            return response

        return response

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        userType = request.POST.get("userType", None)
        user = auth.authenticate(username=username, password=password)


        if user is not None:
            auth.login(request, user)
            if userType is not None:
                refresh = RefreshToken.for_user(user)
                # create cookies
                response = redirect(reverse('app_auth:login_complete', kwargs={'source': 'extension'}))
                response.set_cookie('refresh', str(refresh))
                response.set_cookie('access', str(refresh.access_token))
                return response

            next = request.COOKIES.get('next', None)
            if next:
                slug = request.COOKIES.get('next_args', None)
                response = redirect(reverse(f"{next}", args=[slug]))
                response.delete_cookie('next')
                response.delete_cookie('next_args')
                return response
            messages.add_message(request, messages.SUCCESS, 'Signed in as {}'.format(request.user.username))
            return redirect(reverse("manager:dashboard"))

            
        messages.add_message(request, messages.ERROR, 'Account Not Found.')
        return redirect(reverse("app_auth:login"))

class RegisterUserView(View):
    template_name = "account/register.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username", "")
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if password == confirm_password:
            if not User.objects.filter(username=username):
                User.objects.create_user(username=username, email=email, password=password)
                messages.add_message(request, messages.SUCCESS, 'Account created successfully.')
                return redirect(reverse("app_auth:login"))
            else:
                messages.add_message(request, messages.ERROR, 'Username not available.')
        else:
                messages.add_message(request, messages.ERROR, 'Passwords entered do not match.')

        return render(request, self.template_name)


def logout(request):
    auth.logout(request)
    return redirect(reverse("app_auth:login"))
