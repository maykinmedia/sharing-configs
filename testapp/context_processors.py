from .models import Configuration, Theme


def set_admin_color(request: object) -> dict:
    """
    create a dictionary of color variables to pass to the base_site.html Django admin page
    """
    conf = Configuration.get_solo()
    theme = conf.theme
    if theme is None:
        return {}

    return {
        "primary": theme.primary,
        "secondary": theme.secondary,
        "primary_fg": theme.primary_fg,
        "accent": theme.accent,
    }
