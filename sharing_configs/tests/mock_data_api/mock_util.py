import json
import os


def get_mock_folder() -> str:
    """return path to mock folder"""
    mock_folder_location = os.path.dirname(__file__)
    return mock_folder_location


def get_mock_folders(mode=None) -> dict:
    """return dict containing folders with permission to 'read' for import or 'write' for export"""
    if mode == "export":
        file = "export_expect_folders.json"
    elif mode == "import":
        file = "import_expect_folders.json"
    mock_folder = get_mock_folder()
    path = f"{mock_folder}/{file}"
    if (file is not None) and (mode is not None):
        with open(path) as fh:
            return json.loads(fh.read())


def export_api_response() -> dict:
    """return dict: api response after successful export of an object"""
    file = "export_expect_resp.json"
    mock_folder = get_mock_folder()
    path = f"{mock_folder}/{file}"
    with open(path) as fh:
        return json.loads(fh.read())
