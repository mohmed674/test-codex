def theme(request):
    return {
        "dark_mode_enabled": request.session.get("dark_mode", False)
    }
