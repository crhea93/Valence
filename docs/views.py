from django.shortcuts import render, redirect


def documentation(request):
    context = {}
    return render(request, "build/html/index.html", context=context)
