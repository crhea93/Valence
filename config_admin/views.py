# Create your views here.
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth import get_user_model

import os


def background(request):
    return render(request, "Background.html")


