from .models import Configuration, Theme


def set_admin_color(request: object) -> dict:
    """
    return dict of color options
    """
    conf = Configuration.get_solo()
    color_theme_obj = Theme.objects.filter(theme=conf).last()
    primary_color = color_theme_obj.primary
    secondary_color = color_theme_obj.secondary
    accent = color_theme_obj.accent
    primary_fg = color_theme_obj.primary_fg

    return {
        "primary": primary_color,
        "secondary": secondary_color,
        "primary_fg": primary_fg,
        "accent": accent,
    }
