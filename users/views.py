from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, login = username, password = password)

        if user is not None and user.is_active:
            login(request, user)
            return redirect("main:first_page")

        return render(request, "index/home.html", {
            "login_error": "Неверный логин или пароль"
        })
    return render(request, "index/home.html")

    
@login_required
def logout_view(request):
    logout(request)
    return redirect("main:first_page")




