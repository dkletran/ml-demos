from django.shortcuts import render, redirect

def index(request, route=''):
    return render(
        request,
        'index.html'
    )