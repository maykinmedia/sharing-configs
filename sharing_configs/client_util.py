from urllib.parse import urljoin

import requests

from sharing_configs.models import SharingConfigsConfig

from .exceptions import ApiException


class SharingConfigsClient:
    def __init__(self):
        self.config = SharingConfigsConfig.get_solo()
        self.label = self.config.label
        label_url = f"{str(self.label)}/folder/"
        self.base_url = urljoin(self.config.api_endpoint, label_url)
        # temp token to simulate pet-API
        self.temp_token = "0a8df07c910016e9f8aa047dcd80d4cd945e31e9"
        self.headers = {
            "content-type": "application/json",
            # "authorization": f"Token {self.config.api_key}",
            "authorization": f"token {self.temp_token}",
        }

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
        resp = requests.post(
            url=self.get_export_url(folder), headers=self.headers, json=data
        )
        try:
            resp.raise_for_status()  # status 400<->500
        except requests.exceptions.HTTPError as e:
            raise ApiException("Error during export of object")
        return resp

    def import_data(self, folder: str, filename: str) -> bytes:
        """expect path params: label,folder,filename"""
        resp = requests.get(
            url=self.get_import_url(folder, filename), headers=self.headers
        )
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise ApiException("Error during import of object")
        return resp

    def get_folders(self, permission: dict) -> dict:
        """
        query params: permission(str) and page(int)
        API:{"results":[{"name":"folder_one"},{"name":"folder_two"}],"count":12 ...}
        p.s also possible to generate API error
        """
        print("url", self.get_list_folders_url())
        resp = requests.get(
            url=self.get_list_folders_url(), headers=self.headers, params=permission
        )
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise ApiException({"error": "No folders"})
        return resp

    def get_files(self, folder):
        """
        expect path params: label,folder
        expect query params: page (required)
        api return :{"results":["download_url":"http","filename":".."],"count":12,"next":".","previous":".."}
        """
        resp = requests.get(self.get_folder_files_url(folder), headers=self.headers)
        try:
            resp.raise_for_status()
        except requests.HTTPError as exp:
            raise ApiException("No files available")
        return resp.json()
