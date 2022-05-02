import requests

from sharing_configs.client_util import SharingConfigsClient

from .exceptions import ApiException


def get_folders_from_api(permission: str) -> dict:
    """
    make an API call selecting export or import folders
    ex: {"results":[],count":12,"next":"http...","previous":"http:.."}
    """
    obj = SharingConfigsClient()
    try:
        data = obj.get_folders(permission)
        return data
    except (requests.exceptions.HTTPError, requests.ConnectionError) as exc:
        raise ApiException({"error": "No folders"})


def get_imported_folders_choices(permission: str) -> list:
    """
    create list of tuples (folders name) based on api response
    ex:[('folder_one', 'folder_one'), ('folder_two', 'folder_two')]
    """
    folders_choices = []
    api_dict = get_folders_from_api(permission)
    results_list = api_dict.get("results", None)
    if results_list is not None:
        for folder in results_list:
            folder = folder.get("name", None)
            folders_choices.append((folder, folder))
    else:
        folders_choices = []
    return folders_choices


def get_files_in_folder_from_api(folder: str) -> dict:
    """
    return files for a given folder
    """
    obj = SharingConfigsClient()
    try:
        content = obj.get_files(folder)
        return content
    except requests.exceptions.HTTPError as e:
        raise ApiException


def get_imported_files_choices(folder: str) -> list:
    """
    create list of filenames based on api response and to be passed to js

    """
    api_dict = get_files_in_folder_from_api(folder)
    results_list = api_dict.get("results", None)
    file_choices = []
    if results_list is not None:
        for item in results_list:
            file_choices.append(item.get("filename"))
    return file_choices


class FolderList:
    def __init__(self) -> None:
        self.folders_lst = []

    def folder_collector(self, lst) -> list:
        """
        Take a list and extract all (nested)folders from it.
        """

        for item in lst:
            self.folders_lst.append(item["name"])
            if len(item.get("children")) != 0:
                self.folder_collector(lst=item.get("children"))
        return self.folders_lst
