from .models import Configuration, Theme


def theme(request: object) -> dict:
    """
    Pass the theme to the template context.
    """
    conf = Configuration.get_solo()

    return {"theme": conf.theme}
