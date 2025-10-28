# gabarita_if/context_processors.py
def splash_screen_processor(request):
    show_splash = False
    if request.user.is_authenticated:
        if not request.session.get("splash_seen", False):
            show_splash = True
            request.session["splash_seen"] = True
    return {"show_splash": show_splash}