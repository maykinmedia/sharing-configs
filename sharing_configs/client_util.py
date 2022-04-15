from urllib.parse import urljoin

from django.core.exceptions import ValidationError

import requests

from .models import SharingConfigsConfig


class SharingConfigsClient:
    def __init__(self):
        self.config = SharingConfigsConfig.get_solo()
        self.label = self.config.label
        self.base_url = urljoin(self.config.api_endpoint, f"{self.label}/folder")

    def get_list_folders_url(self):
        """url to get available folders and subfolders"""
        return self.base_url

    def get_folder_files_url(self, folder):
        """get files in a given folder"""
        return urljoin(self.base_url, f"{folder}/files/")

    def get_import_url(self, folder, filename):
        """get a given file"""
        return urljoin(self.base_url, f"{folder}/files/{filename}/")

    def get_export_url(self, folder):
        """get url to upload a file"""
        return urljoin(self.base_url, f"{folder}/files/")

    def export(self, folder, data):
        """
        expect path params:label,folder
        body: filename(str),content(str),author(str),overwrite
        """
        headers = {
            "content-type": "application/json",
            "authorization": f"Token {self.config.api_key}",
        }
        try:
            resp = requests.post(
                self.get_export_url(folder), headers=headers, data=data
            )
            content = resp.json()
            if resp.status_code == 200:
                return content
        except requests.exceptions.RequestException as err:
            print("Smth went wrong. Resp status != 200")
            return {}

    def import_data(self, folder: str, filename: str) -> bytes:
        """expect path params: label,folder,filename"""
        headers = {
            "content-type": "application/json",
            "authorization": f"Token {self.config.api_key}",
        }
        try:
            resp = requests.get(
                url=self.get_import_url(folder, filename), headers=headers
            )
            content = resp.json()
            if resp.status_code == 200:
                # user gets a binary
                # return content
                return {"msg": "Import successful.Binary here"}

        except requests.exceptions.RequestException as err:
            # print("This url does not exist", err)
            return {}

    def get_folders(self, permission: dict) -> dict:
        """
        query params: permission(str) and page(int)
        API:{"results":[{"name":"folder_one"},{"name":"folder_two"}],"count":12 ...}
        """
        headers = {
            "content-type": "application/json",
            "authorization": f"Token {self.config.api_key}",
        }
        try:
            resp = requests.get(
                url=self.get_list_folders_url(), headers=headers, params=permission
            )
            content = resp.json()
            if resp.status_code == 200:
                # print("status OK, you've got your dict", content)
                return content
        except requests.exceptions.RequestException as err:
            print("This url does not exist", err)
            return {}

    def get_files(self, folder):
        """
        expect path params: label,folder
        expect query params: page (required)
        api return :{"results":["download_url":"http","filename":".."],"count":12,"next":".","previous":".."}
        """
        print("line 93 folder is", folder)
        headers = {
            "content-type": "application/json",
            "authorization": f"Token {self.config.api_key}",
        }

        try:
            resp = requests.get(self.get_folder_files_url(folder), headers=headers)
            content = resp.json()
            if resp.status_code == 200:
                print("list of files is here")
                return content
        except:
            print("resp status != 200 ")
