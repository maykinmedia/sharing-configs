import base64
from typing import Optional

from sharing_configs.client_util import SharingConfigsClient


def get_imported_folders_choices(permission: Optional[str]) -> list:
    """
    create list of tuples (folders name) based on api response
    ex:[('folder_one', 'folder_one'), ('folder_two', 'folder_two')]
    """
    client = SharingConfigsClient()

    api_dict = client.get_folders(permission)
    results_list = api_dict.get("results", "No results in your dict")
    folders_choices = []
    if results_list is not None:
        lst = FolderList()
        all_folders = lst.folder_collector(results_list)
        for folder in all_folders:
            folders_choices.append((folder, folder))

    return folders_choices


def get_folders(permission: Optional[str]) -> list:
    """
        results:
    [{'name': 'community-producten', 'children': [], 'permission': 'write'},
    {'name': 'voorbeeld-producten', 'children': [], 'permission': 'read'}]
    """
    client = SharingConfigsClient()

    api_dict = client.get_folders(permission)
    results = api_dict.get("results", "No results in your dict")
    return results


def get_imported_files_choices(folder: str) -> list:
    """
    create list of filenames based on api response and to be passed to js

    """
    client = SharingConfigsClient()

    api_dict = client.get_files(folder)
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


def get_str_from_encoded64_object(content: bytes) -> str:
    """return string as a result of decoding (base64) byte object"""
    return base64.b64encode(content).decode("utf-8")
