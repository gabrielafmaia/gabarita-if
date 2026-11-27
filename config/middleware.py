from django.utils.cache import patch_vary_headers


class HtmxBoostedVaryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.get("Content-Type", "").startswith("text/html"):
            patch_vary_headers(response, ("HX-Request", "HX-Boosted"))
        return response
