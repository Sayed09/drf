from django.http import JsonResponse


# custom json response for page not found
def error404(request, exception):
    return JsonResponse({"Message": "Page not found", "code": "PNF404"}, status=404)
