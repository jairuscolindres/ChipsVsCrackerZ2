from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
# Create your views here.

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        password2 = request.POST.get("password2")

        if password != password2:
            return render(request, "register/register.html", {
                "error": "Passwords do not match"
            })

        if User.objects.filter(username=username).exists():
            return render(request, "register/register.html", {
                "error": "Username already taken"
            })

        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect("home:home")

    return render(request, "register/register.html")
