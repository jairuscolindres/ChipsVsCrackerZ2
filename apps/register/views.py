from django.shortcuts import render, redirect
from django.contrib.auth.models import User
# Create your views here.
from django.contrib.auth import login as auth_login

def register_view(request):
    if request.user.is_authenticated:
        return redirect("home:home")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not password:
            return render(request, "register/register.html", {
                "error": "Operator callsign and security key are required."
            })
        if confirm_password and password != confirm_password:
            return render(request, "register/register.html", {
                "error": "Security key verification mismatch."
            })
        if User.objects.filter(username=username).exists():
            return render(request, "register/register.html", {
                "error": f"Operator callsign '{username}' is already registered."
            })
        user = User.objects.create_user(
            username=username,
            password=password
        )
        auth_login(request, user)
        return redirect("home:home")
    return render(request, "register/register.html")
