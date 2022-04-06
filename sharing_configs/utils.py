import json
import os

from django.conf import settings
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


def get_folders_from_api(params) -> dict:
    """
    make an API call using query params selecting export and import folders
    """
    try:
        # TODO:here get API call to fetch list of folders for a given user
        api_url = "https://api.com/"
        url = api_url + params
        with open(os.path.join(settings.BASE_DIR, "mock_data/folders.json")) as fh:
            data = json.load(fh)
            return data
    except FileNotFoundError:
        # return error msg from API point
        print("file not found,return empty {}")
        return {"error": "no data"}
    # for using real external API
    except requests.exceptions.ConnectionError as err:
        print("Error Connecting:", err)
    except requests.exceptions.Timeout:
        print("Timeout Error. Try again?")
    except requests.exceptions.HTTPError as err:
        print("HTTP greet : Something Else", err)
    except requests.exceptions.RequestException as err:
        print("Final (unknown) error", err)


def get_imported_folders_choices(params) -> list:
    """
    create list of tuples (for folders) from based on  dict api response;
    pass params to create a query in url
    """
    api_list_folders = get_folders_from_api(params)
    folders_choices = []
    try:
        for folder in api_list_folders["data"]:
            folders_choices.append((folder, folder))
    except Exception as e:
        # print("exeption block", e) # form_folder_field[1]
        return e
    # [('folder_one', 'folder_one'), ('folder_two', 'folder_two')]
    return folders_choices


def get_files_in_folder_from_api(folder) -> dict:
    """
    mock an API call (list of available files in a given folder )
    from testapp/mock_data/files_folder_x
    return files for a given folder
    """
    if folder == "folder_one":
        path = "mock_data/folders/files_folder_1.json"
    elif folder == "folder_two":
        path = "mock_data/folders/files_folder_2.json"
    else:
        print("no folder, no path")
    try:
        with open(os.path.join(settings.BASE_DIR, path)) as fh:
            data = json.load(fh)
            return data
    # for using json file mocking external API
    except FileNotFoundError:
        # return error msg from API
        return {}
    except MemoryError:
        # file is too big
        return {}
    # for using real external API
    except requests.exceptions.ConnectionError as err:
        print("Error Connecting:", err)
    except requests.exceptions.Timeout:
        print("Timeout Error. Try again?")
    except requests.exceptions.HTTPError as err:
        print("HTTP greet : Something Else", err)
    except requests.exceptions.RequestException as err:
        print("Final (unknown) error", err)


def get_imported_files_choices(folder) -> list:
    """
    create list of files from parsing dict (api response)
    """
    api_list_files = get_files_in_folder_from_api(folder)
    file_choices = []
    for file in api_list_files["data"]:
        file_choices.append((file))
    return file_choices
