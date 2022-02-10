from django.core.exceptions import ValidationError

import requests


def download_file(url: str) -> bytes:
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException:
        raise ValidationError("The url does not exist.")

    if response.status_code != requests.codes.ok:
        raise ValidationError("The url returned non OK status.")

    return response.content
