from django.http import HttpResponse


def example(request):
    res = request.GET.get('i')
    if res:
        res = int(res)
    return HttpResponse("Hello, world!")
