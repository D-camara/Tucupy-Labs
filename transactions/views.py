from django.http import HttpResponse


def placeholder(_request):
    return HttpResponse("transactions ok")

