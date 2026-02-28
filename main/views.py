from django.shortcuts import render, get_object_or_404
from main.models import Profile
from django.contrib.auth.models import User

def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = Profile.objects.get_or_create(user=user)
    context = {
        "user": user,
        "profile": profile
    }
    return render(request, "profile.html", context)