from django.http import HttpResponse


def placeholder(_request):  # Simple placeholder view for wiring tests
    return HttpResponse("accounts ok")

