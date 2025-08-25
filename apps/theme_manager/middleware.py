class ThemeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # اقرأ من الـ session أو اجعل الوضع الافتراضي Light
        request.theme = request.session.get("theme", "light")
        return self.get_response(request)
