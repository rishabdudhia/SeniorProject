from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

def say_hello(request):
    return HttpResponse("Hello World")

def json_get(request):
    if request.method == 'GET':
        return JsonResponse({"name":"rishab"})