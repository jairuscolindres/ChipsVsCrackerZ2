from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
# Create your views here.

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home:home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("home:home")

        return render(request, "login/login.html", {
            "error": "Access Denied: Checksum mismatch or invalid operator credentials."
        })
    return render(request, "login/login.html")

