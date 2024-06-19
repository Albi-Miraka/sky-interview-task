import logging
from _pydatetime import datetime
from dataclasses import dataclass
from enum import Enum
from typing import List, Any


class ResultType(Enum):
    ASSET = 'ASSET'
    RIGHT = 'RIGHT'


@dataclass
class Endpoint:
    origin: str
    path: str

    @staticmethod
    def from_dict(endpoint: Any) -> 'Endpoint':
        _origin = str(endpoint.get("origin"))
        _path = str(endpoint.get("path"))
        return Endpoint(_origin, _path)

    def print_path(self):
        logging.info(self.path)


@dataclass
class Asset:
    endpoints: List[Endpoint]
    video_format: str

    @staticmethod
    def from_dict(asset: Any) -> 'Asset':
        _endpoints = [Endpoint.from_dict(elem) for elem in asset.get("endpoints")]
        _video_format = str(asset.get("videoFormat"))
        return Asset(_endpoints, _video_format)

    def is_video_format_HD_and_origin_level3(self) -> 'bool':
        found: bool = False
        if self.video_format == "HD" and self.endpoints[0].origin == "level3":
            found = True
        return found


@dataclass
class Device:
    device_platform: str
    device_type: str
    provider: str

    @staticmethod
    def from_dict(device: Any) -> 'Device':
        _device_platform = str(device.get("devicePlatform"))
        _device_type = str(device.get("deviceType"))
        _provider = str(device.get("provider"))
        return Device(_device_platform, _device_type, _provider)


@dataclass
class Term:
    start_date_time: datetime
    end_date_time: datetime
    territory: str
    devices: List[Device]

    @staticmethod
    def from_dict(term: Any) -> 'Term':
        _start_date_time = datetime.fromisoformat(term.get("startDateTime"))
        _end_date_time = datetime.fromisoformat(term.get("endDateTime"))
        _territory = str(term.get("channel"))
        _devices = [Device.from_dict(elem) for elem in term.get("devices")]
        return Term(_start_date_time, _end_date_time, _territory, _devices)

    def is_active(self) -> 'bool':
        return self.start_date_time.replace(tzinfo=None) <= datetime.now() <= self.end_date_time.replace(tzinfo=None)

    def can_be_played_on_device(self, device_attribute: str, expected_value: str) -> 'bool':
        can_be_played: bool = False
        for device in self.devices:
            if device.__getattribute__(device_attribute) is not None and device.__getattribute__(device_attribute) == expected_value:
                can_be_played = True
        return can_be_played

    def can_be_played_on_ROKU(self) -> bool:
        return self.can_be_played_on_device("device_platform", "ROKU")


@dataclass
class LocalizableInformation:
    locale: str
    language: str
    title_name_medium: str

    @staticmethod
    def from_dict(localizable_information: Any) -> 'LocalizableInformation':
        _locale = str(localizable_information.get("locale"))
        _language = str(localizable_information.get("language"))
        _title_name_medium = str(localizable_information.get("titleNameMedium"))
        return LocalizableInformation(_locale, _language, _title_name_medium)


@dataclass
class Right:
    channel: str
    terms: List[Term]

    @staticmethod
    def from_dict(right: Any) -> 'Right':
        _channel = str(right.get("channel"))
        _terms = [Term.from_dict(elem) for elem in right.get("terms")]
        return Right(_channel, _terms)


@dataclass
class ResultAsset:
    content_id: str
    access_channel: str
    assets: List[Asset]

    @staticmethod
    def from_dict(result: Any) -> 'ResultAsset':
        _content_id = str(result.get("contentId"))
        _access_channel = str(result.get("accessChannel"))
        _assets = [Asset.from_dict(elem) for elem in result.get("assets")]
        return ResultAsset(_content_id, _access_channel, _assets)

    def print_path(self):
        for asset in self.assets:
            print(asset.endpoints[0].path)


@dataclass
class ResultRights:
    content_id: str
    access_channel: str
    localizable_information: List[LocalizableInformation]
    rights: Right

    @staticmethod
    def from_dict(result: Any) -> 'ResultRights':
        _content_id = str(result.get("contentId"))
        _access_channel = str(result.get("accessChannel"))
        _localizable_information = [LocalizableInformation.from_dict(elem) for elem in
                                    result.get("localizableInformation")]
        _rights = Right.from_dict(result.get("rights"))
        return ResultRights(_content_id, _access_channel, _localizable_information, _rights)

    def print_title_name_medium(self):
        logging.info(self.localizable_information[0].title_name_medium)


@dataclass
class Response:
    results: List[Any]

    @staticmethod
    def from_dict(response: Any, result_type: ResultType) -> 'Response':
        match result_type:
            case ResultType.ASSET:
                _results = [ResultAsset.from_dict(elem) for elem in response.get("results")]
                return Response(_results)
            case ResultType.RIGHT:
                _results = [ResultRights.from_dict(elem) for elem in response.get("results")]
                return Response(_results)


def print_title_name_medium(result_right: List[ResultRights], header: str = None):
    if header is not None:
        logging.info(header)
    for result in result_right:
        result.print_title_name_medium()


def print_endpoints(endpoints: List[Endpoint], header: str = None):
    if header is not None:
        logging.info(header)
    for endpoint in endpoints:
        endpoint.print_path()


def filter_result_by_active_data_and_video_format_and_endpoint_origin_level(result_asset: List[ResultAsset], contend_ids: List[str]) -> 'List[Endpoint]':
    active_data = [result for result in result_asset if contend_ids.__contains__(result.content_id)]
    endpoints = []
    for result in active_data:
        for asset in result.assets:
            if asset.is_video_format_HD_and_origin_level3():
                endpoints.append(asset.endpoints[0])
    return endpoints


def filter_result_by_active(result_asset: List[ResultRights]) -> 'List[ResultRights]':
    return [result for result in result_asset if result.rights.terms[0].is_active()]


def filter_result_by_can_be_played_on_ROKU(result_asset: List[ResultRights]) -> 'List[ResultRights]':
    return [result for result in result_asset if result.rights.terms[0].can_be_played_on_ROKU()]
