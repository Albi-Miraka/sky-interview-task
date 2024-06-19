import json
import unittest
from _pydatetime import datetime
from typing import List

from src.main import Result
from src.main.Result import Endpoint, Asset, Device, Term, LocalizableInformation, Right, ResultAsset, ResultRights


class MyTestCase(unittest.TestCase):

    def test_from_dict_of_Endpoint(self):
        # DATA TO ASSERT
        expected_endpoint: Endpoint = Endpoint("akamai", "/skyplayer/akamai/sky-test-id-1/hd/Manifest")
        endpoint_json = """
            {
                "origin": "akamai",
                "path": "/skyplayer/akamai/sky-test-id-1/hd/Manifest"
            }
        """
        parsed_endpoint: Endpoint = Endpoint.from_dict(json.loads(endpoint_json))
        self.assertEqual(expected_endpoint, parsed_endpoint)

        # WITH NO DATA
        expected_endpoint: Endpoint = Endpoint(None, None)
        endpoint_json = """{}"""
        parsed_endpoint: Endpoint = Endpoint.from_dict(json.loads(endpoint_json))
        self.assertEqual(expected_endpoint, parsed_endpoint)

    def test_from_dict_of_Asset(self):
        # DATA TO ASSERT
        expected_asset: Asset = Asset([Endpoint("level3", "/skyplayer/level3/sky-test-id-1/hd/Manifest")], "HD")
        asset_json = """
            {
                "endpoints": [
                    {
                        "origin": "level3",
                        "path": "/skyplayer/level3/sky-test-id-1/hd/Manifest"
                    }
                ],
                "videoFormat": "HD"
            }
        """
        parsed_asset: Asset = Asset.from_dict(json.loads(asset_json))
        self.assertEqual(expected_asset, parsed_asset)

        # IS ACCEPTED TO HAS NONE DATA
        expected_asset: Asset = Asset(None, None)
        asset_json = """{}"""
        parsed_asset: Asset = Asset.from_dict(json.loads(asset_json))
        self.assertEqual(expected_asset, parsed_asset)

        # RAISE ERROR IF ENDPOINT HAS MORE THE 1 ITEM
        asset_json = """
            {
                "endpoints": [
                    {
                        "origin": "level3",
                        "path": "/skyplayer/level3/sky-test-id-1/hd/Manifest"
                    },
                    {
                        "origin": "level3",
                        "path": "/skyplayer/level3/sky-test-id-1/hd/Manifest"
                    }
                ],
                "videoFormat": "HD"
            }
        """
        with self.assertRaises(ValueError):
            Asset.from_dict(json.loads(asset_json))

    def test_is_video_format_HD_and_origin_level3(self):
        # TRUE CASE -> WHEN video_format = HD and endpoint.origin = level3
        asset: Asset = Asset([Endpoint("level3", "/skyplayer/level3/sky-test-id-1/hd/Manifest")], "HD")
        self.assertTrue(asset.is_video_format_HD_and_origin_level3())

        # FALSE CASES
        asset: Asset = Asset([], "HD")
        self.assertFalse(asset.is_video_format_HD_and_origin_level3())
        asset: Asset = Asset(None, "HD")
        self.assertFalse(asset.is_video_format_HD_and_origin_level3())
        asset: Asset = Asset([Endpoint("level3", "/skyplayer/level3/sky-test-id-1/hd/Manifest")], "SD")
        self.assertFalse(asset.is_video_format_HD_and_origin_level3())
        asset: Asset = Asset([Endpoint("akamai", "/skyplayer/level3/sky-test-id-1/hd/Manifest")], "SD")
        self.assertFalse(asset.is_video_format_HD_and_origin_level3())

    def test_from_dict_of_Device(self):
        # DATA TO ASSERT
        expected_device: Device = Device("SAMSUNG", "TV", "SKY")
        device_json = """
            {
                "devicePlatform": "SAMSUNG",
                "deviceType": "TV",
                "provider": "SKY"
            }
        """
        parsed_device: Device = Device.from_dict(json.loads(device_json))
        self.assertEqual(expected_device, parsed_device)

        # DATA TO ASSERT
        expected_device: Device = Device(None, None, None)
        device_json = """{}"""
        parsed_device: Device = Device.from_dict(json.loads(device_json))
        self.assertEqual(expected_device, parsed_device)

    def test_from_dict_of_Term(self):
        # DATA TO ASSERT
        expected_term: Term = Term(datetime.fromisoformat("2024-05-02T23:00:00.000Z"),
                                   datetime.fromisoformat("2025-06-14T22:00:00.000Z"), "GB",
                                   [Device("XBOX", "CONSOLE", "NOWTV")])
        term_json = """
            {
                "startDateTime": "2024-05-02T23:00:00.000Z",
                "endDateTime": "2025-06-14T22:00:00.000Z",
                "territory": "GB",
                "devices": [
                    {
                        "devicePlatform": "XBOX",
                        "deviceType": "CONSOLE",
                        "provider": "NOWTV"
                    }
                ]
            }
        """
        parsed_term: Term = Term.from_dict(json.loads(term_json))
        self.assertEqual(expected_term, parsed_term)

        # RAISE ERROR IF start_date_time OR end_date_time IS None
        term_json = """
            {
                "startDateTime": "2024-05-02T23:00:00.000Z",
            }
        """
        with self.assertRaises(ValueError):
            Term.from_dict(json.loads(term_json))

        term_json = """
            {
                "endDateTime": "2024-05-02T23:00:00.000Z",
            }
        """
        with self.assertRaises(ValueError):
            Term.from_dict(json.loads(term_json))

    def test_is_active(self):
        # TRUE CASE -> WHEN currentDate is between startDate and endDate
        term: Term = Term(datetime.fromisoformat("2024-05-02T23:00:00.000Z"),
                          datetime.fromisoformat("2025-06-14T22:00:00.000Z"), None, None)
        self.assertTrue(term.is_active())

        # FALSE CASES
        term: Term = Term(datetime.fromisoformat("2025-05-02T23:00:00.000Z"),
                          datetime.fromisoformat("2025-06-14T22:00:00.000Z"), None, None)
        self.assertFalse(term.is_active())
        term: Term = Term(datetime.fromisoformat("2024-05-02T23:00:00.000Z"),
                          datetime.fromisoformat("2024-06-14T22:00:00.000Z"), None, None)
        self.assertFalse(term.is_active())

    def test_can_be_played_on_device(self):
        # TRUE CASE -> WHEN device_attribute exists and is equal to expected_value
        term: Term = Term(datetime.fromisoformat("2024-05-02T23:00:00.000Z"),
                          datetime.fromisoformat("2025-06-14T22:00:00.000Z"), None,
                          [Device("XBOX", "CONSOLE", "NOWTV")])
        self.assertTrue(term.can_be_played_on_device("provider", "NOWTV"))
        self.assertTrue(term.can_be_played_on_device("device_type", "CONSOLE"))
        self.assertTrue(term.can_be_played_on_device("device_platform", "XBOX"))
        self.assertFalse(term.can_be_played_on_device("device_platform", "NOWTV"))

        # RAISE CASE -> if devices is None or empty or device_attribute doesn't exist
        with self.assertRaises(AttributeError):
            term.can_be_played_on_device("not_existing_device_attribute", "no")

    def test_can_be_played_on_ROKU(self):
        # TRUE CASE -> WHEN device has device_platform equals to ROKU
        term: Term = Term(datetime.fromisoformat("2024-05-02T23:00:00.000Z"),
                          datetime.fromisoformat("2025-06-14T22:00:00.000Z"), None,
                          [Device("XBOX", "CONSOLE", "ROKU")])

        self.assertTrue(term.can_be_played_on_ROKU())

        # FALSE CASE
        term: Term = Term(datetime.fromisoformat("2024-05-02T23:00:00.000Z"),
                          datetime.fromisoformat("2025-06-14T22:00:00.000Z"), None,
                          [Device("XBOX", "CONSOLE", "NOWTV")])

        self.assertFalse(term.can_be_played_on_ROKU())

    def test_from_dict_of_LocalizableInformation(self):
        # DATA TO ASSERT
        expected_localizable_information: LocalizableInformation = LocalizableInformation("en-GB", "eng",
                                                                                          "A Man Called Otto")
        localizable_information_json = """
            {
                "locale": "en-GB",
                "language": "eng",
                "titleNameMedium": "A Man Called Otto"
            }
        """
        parsed_localizable_information: LocalizableInformation = LocalizableInformation.from_dict(
            json.loads(localizable_information_json))
        self.assertEqual(expected_localizable_information, parsed_localizable_information)

        # DATA TO ASSERT
        expected_localizable_information: LocalizableInformation = LocalizableInformation(None, None, None)
        localizable_information_json = """{}"""
        parsed_localizable_information: LocalizableInformation = LocalizableInformation.from_dict(
            json.loads(localizable_information_json))
        self.assertEqual(expected_localizable_information, parsed_localizable_information)

    def test_from_dict_of_Right(self):
        # DATA TO ASSERT
        expected_right: Right = Right("hdr.cinema.sky.com", [Term(datetime.fromisoformat("2023-08-10T23:00:00.000Z"),
                                                                  datetime.fromisoformat("2024-10-12T22:59:59.000Z"),
                                                                  None, None)])
        right_json = """
            {
                "channel": "hdr.cinema.sky.com",
                "terms": [
                    {
                        "startDateTime": "2023-08-10T23:00:00.000Z",
                        "endDateTime": "2024-10-12T22:59:59.000Z"
                    }
                ]
            }
        """

        parsed_right: Right = Right.from_dict(json.loads(right_json))
        self.assertEqual(expected_right, parsed_right)

        # None Cases
        expected_right: Right = Right(None, None)
        right_json = """{}"""
        parsed_right: Right = Right.from_dict(json.loads(right_json))
        self.assertEqual(expected_right, parsed_right)

        # RAISE ERROR IF terms has more than 1 item
        right_json = """
            {
                "channel": "hdr.cinema.sky.com",
                "terms": [
                    {
                        "startDateTime": "2023-08-10T23:00:00.000Z",
                        "endDateTime": "2024-10-12T22:59:59.000Z"
                    },
                    {
                        "startDateTime": "2023-08-10T23:00:00.000Z",
                        "endDateTime": "2024-10-12T22:59:59.000Z"
                    }
                ]
            }
        """
        with self.assertRaises(ValueError):
            Right.from_dict(json.loads(right_json))

    def test_from_dict_of_ResultAsset(self):
        # DATA TO ASSERT
        expected_result_asset: ResultAsset = ResultAsset("sky-test-id-1", "itv3", [
            Asset([Endpoint("level3", "/skyplayer/level3/sky-test-id-1/sd/Manifest")], "SD")
        ])
        result_asset_json = """
            {
                "contentId": "sky-test-id-1",
                "accessChannel": "itv3",
                "assets": [
                    {
                        "endpoints": [
                            {
                                "origin": "level3",
                                "path": "/skyplayer/level3/sky-test-id-1/sd/Manifest"
                            }
                        ],
                        "videoFormat": "SD"
                    }
                ]
            }
        """

        parsed_result_asset: ResultAsset = ResultAsset.from_dict(json.loads(result_asset_json))
        self.assertEqual(expected_result_asset, parsed_result_asset)

        # DATA TO ASSERT
        expected_result_asset: ResultAsset = ResultAsset("sky-test-id-1", None, [Asset(None, "SD")])
        result_asset_json = """
            {
                "contentId": "sky-test-id-1",
                "assets": [
                    {
                        "videoFormat": "SD"
                    }
                ]
            }
        """

        parsed_result_asset: ResultAsset = ResultAsset.from_dict(json.loads(result_asset_json))
        self.assertEqual(expected_result_asset, parsed_result_asset)

        expected_result_asset: ResultAsset = ResultAsset("sky-test-id-1", None, None)
        result_asset_json = """
            {
                "contentId": "sky-test-id-1"
            }
        """

        parsed_result_asset: ResultAsset = ResultAsset.from_dict(json.loads(result_asset_json))
        self.assertEqual(expected_result_asset, parsed_result_asset)

        # RAISE ERROR IF content_id is None
        result_asset_json = """{}"""
        with self.assertRaises(ValueError):
            ResultAsset.from_dict(json.loads(result_asset_json))

    def test_from_dict_of_ResultRights(self):
        expected_result_right: ResultRights = ResultRights("sky-test-id-1", "itv3", [
            LocalizableInformation("en-GB", "eng", "Agatha Christie's Marple")
        ], Right("itv3.itv.com", [
            Term(datetime.fromisoformat("2024-05-31T16:48:47.000Z"), datetime.fromisoformat("2024-10-30T22:59:00.000Z"),
                 "GB", [Device("APPLETV", "IPSETTOPBOX", "SKY")])
        ]))
        result_right_json = """
            {
                "contentId": "sky-test-id-1",
                "accessChannel": "itv3",
                "localizableInformation": [
                    {
                        "locale": "en-GB",
                        "language": "eng",
                        "titleNameMedium": "Agatha Christie's Marple"
                    }
                ],
                "rights": {
                    "channel": "itv3.itv.com",
                    "terms": [
                        {
                            "startDateTime": "2024-05-31T16:48:47.000Z",
                            "endDateTime": "2024-10-30T22:59:00.000Z",
                            "territory": "GB",
                            "devices": [
                                {
                                    "devicePlatform": "APPLETV",
                                    "deviceType": "IPSETTOPBOX",
                                    "provider": "SKY"
                                }
                            ]
                        }
                    ]
                }
            }
        """

        parsed_result_rights: ResultRights = ResultRights.from_dict(json.loads(result_right_json))
        self.assertEqual(expected_result_right, parsed_result_rights)

        # RAISE ERROR IF content_id is None
        result_right_json = """{}"""
        with self.assertRaises(ValueError):
            ResultRights.from_dict(json.loads(result_right_json))

    def test_filter_result_by_active_data_and_video_format_and_endpoint_origin_level(self):
        list_of_result_assets: List[ResultAsset] = [ResultAsset("1", None, [
            Asset([Endpoint("level3", "path")], "HD"), Asset([Endpoint("level3", "path")], "SD")
        ]), ResultAsset("2", None, [
            Asset([Endpoint("level3", "path")], "HD"), Asset([Endpoint("level3", "path")], "SD")
        ])]

        list_of_content_id: List[str] = ["1"]

        list_of_filtered_endpoints: List[Endpoint] = (
            Result.filter_result_by_active_data_and_video_format_and_endpoint_origin_level(
                list_of_result_assets, list_of_content_id))

        # EXPECTING JUST 1 ENDPOINT, BECAUSE THE SECOND ITEM OF list_of_result_assets HAS content_id = 2 THAT IS NOT
        # PART OF list_of_content_id, AND Asset([Endpoint("level3", "path")], "SD") HAS video_format SD
        self.assertTrue(list_of_filtered_endpoints.__len__() == 1)
        self.assertEqual(list_of_filtered_endpoints[0], Endpoint("level3", "path"))


if __name__ == '__main__':
    unittest.main()
