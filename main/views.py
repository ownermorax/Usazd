from django.shortcuts import render, get_object_or_404, redirect
from main.models import Profile
from django.contrib.auth.models import User
from django.contrib.auth import login
from main.forms import RegistrationForm

def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    context = {
        "user": user,
        "profile": profile
    }
    return render(request, "profile.html", context)

def reg(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = RegistrationForm()

    return render(request, "registration/reg.html", {'form': form})

def index(request):
    return render(request,'index.html')