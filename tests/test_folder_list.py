from django.test import TestCase

from sharing_configs.utils import FolderList


class MyFolderCollecorTest(TestCase):
    """Test collecting all folders and sub-folders from json"""

    def test_one_root_parent(self):
        lst_one = [
            {
                "name": "parent-folder1",
                "children": [
                    {
                        "name": "sub-folder-1.1",
                        "children": [{"name": "sub-folder-1.2", "children": []}],
                    }
                ],
            }
        ]
        expected_list = ["parent-folder1", "sub-folder-1.1", "sub-folder-1.2"]
        folders_search = FolderList()

        calc_collection = folders_search.folder_collector(lst_one)

        self.assertEqual(len(calc_collection), 3)
        self.assertEqual(expected_list, calc_collection)

    def test_two_root_parents(self):
        lst_two = [
            {
                "name": "parent-folder1",
                "children": [
                    {
                        "name": "sub-folder-1.1",
                        "children": [{"name": "sub-folder-1.2", "children": []}],
                    }
                ],
            },
            {
                "name": "parent-folder2",
                "children": [
                    {
                        "name": "sub-folder-2.1",
                        "children": [{"name": "sub-folder-2.2", "children": []}],
                    }
                ],
            },
        ]
        expected_list = [
            "parent-folder1",
            "sub-folder-1.1",
            "sub-folder-1.2",
            "parent-folder2",
            "sub-folder-2.1",
            "sub-folder-2.2",
        ]

        folders_search = FolderList()

        calc_collection = folders_search.folder_collector(lst_two)

        self.assertEqual(len(calc_collection), 6)
        self.assertEqual(expected_list, calc_collection)

    def test_one_root_many_nested(self):
        lst_four = [
            {
                "name": "root-folder1",
                "children": [
                    {
                        "name": "sub-folder-1.1",
                        "children": [
                            {
                                "name": "sub-folder-1.2",
                                "children": [
                                    {
                                        "name": "sub-folder-1.2.1",
                                        "children": [
                                            {
                                                "name": "sub-folder-1.2.1.1",
                                                "children": [],
                                            }
                                        ],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
        ]
        expected_list = [
            "root-folder1",
            "sub-folder-1.1",
            "sub-folder-1.2",
            "sub-folder-1.2.1",
            "sub-folder-1.2.1.1",
        ]
        folders_search = FolderList()

        calc_collection = folders_search.folder_collector(lst_four)

        self.assertEqual(len(calc_collection), 5)
        self.assertEqual(calc_collection, expected_list)
