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
    origin: str | None
    path: str | None

    @staticmethod
    def from_dict(endpoint: Any) -> 'Endpoint':
        _origin = None if endpoint.get("origin") is None else str(endpoint.get("origin"))
        _path = None if endpoint.get("path") is None else str(endpoint.get("path"))
        return Endpoint(_origin, _path)

    def print_path(self):
        if self.path is None or self.path == '':
            logging.warning("No information available")
        else:
            logging.info(self.path)


@dataclass
class Asset:
    endpoints: List[Endpoint] | None
    video_format: str | None

    @staticmethod
    def from_dict(asset: Any) -> 'Asset':
        # Check validity of endpoints
        if asset.get("endpoints") is not None and asset.get("endpoints").__len__() > 1:
            raise ValueError("From Assertions endpoints has to be an array with JUST one value:\nData: [%s]",
                             asset.get("endpoints"))
        _endpoints = None if asset.get("endpoints") is None else [Endpoint.from_dict(elem) for elem in
                                                                  asset.get("endpoints")]

        _video_format = None if asset.get("videoFormat") is None else str(asset.get("videoFormat"))
        return Asset(_endpoints, _video_format)

    def is_video_format_HD_and_origin_level3(self) -> 'bool':
        if (self.endpoints is None or self.endpoints.__len__() == 0 or self.endpoints[0].origin is None
                or self.video_format is None):
            return False

        found: bool = False
        if self.video_format == "HD" and self.endpoints[0].origin == "level3":
            found = True
        return found


@dataclass
class Device:
    device_platform: str | None
    device_type: str | None
    provider: str | None

    @staticmethod
    def from_dict(device: Any) -> 'Device':
        _device_platform = None if device.get("devicePlatform") is None else str(device.get("devicePlatform"))
        _device_type = None if device.get("deviceType") is None else str(device.get("deviceType"))
        _provider = None if device.get("provider") is None else str(device.get("provider"))
        return Device(_device_platform, _device_type, _provider)


@dataclass
class Term:
    start_date_time: datetime
    end_date_time: datetime
    territory: str | None
    devices: List[Device] | None

    @staticmethod
    def from_dict(term: Any) -> 'Term':
        if term.get("startDateTime") is None or term.get("endDateTime") is None:
            raise ValueError(
                "From Assertions startDateTime and endDateTime has both required:\nData startDateTime:[%s] - endDateTime:[%s]",
                term.get("startDateTime"), term.get("endDateTime"))
        _start_date_time = datetime.fromisoformat(term.get("startDateTime"))
        _end_date_time = datetime.fromisoformat(term.get("endDateTime"))

        _territory = None if term.get("territory") is None else str(term.get("territory"))
        _devices = None if term.get("devices") is None else [Device.from_dict(elem) for elem in term.get("devices")]
        return Term(_start_date_time, _end_date_time, _territory, _devices)

    def is_active(self) -> 'bool':
        return self.start_date_time.replace(tzinfo=None) <= datetime.now() <= self.end_date_time.replace(tzinfo=None)

    def can_be_played_on_device(self, device_attribute: str, expected_value: str) -> 'bool':
        if self.devices is None or self.devices.__len__() == 0:
            return False

        can_be_played: bool = False
        for device in self.devices:
            if device.__getattribute__(device_attribute) is not None and device.__getattribute__(
                    device_attribute) == expected_value:
                can_be_played = True
        return can_be_played

    def can_be_played_on_ROKU(self) -> bool:
        return self.can_be_played_on_device("provider", "ROKU")


@dataclass
class LocalizableInformation:
    locale: str | None
    language: str | None
    title_name_medium: str | None

    @staticmethod
    def from_dict(localizable_information: Any) -> 'LocalizableInformation':
        _locale = None if localizable_information.get("locale") is None else str(localizable_information.get("locale"))
        _language = None if localizable_information.get("language") is None \
            else str(localizable_information.get("language"))
        _title_name_medium = None if localizable_information.get("titleNameMedium") is None \
            else str(localizable_information.get("titleNameMedium"))
        return LocalizableInformation(_locale, _language, _title_name_medium)


@dataclass
class Right:
    channel: str | None
    terms: List[Term] | None

    @staticmethod
    def from_dict(right: Any) -> 'Right':
        if right.get("terms") is not None and right.get("terms").__len__() > 1:
            raise ValueError("From Assertions rights has to be an array with JUST one value:\nData: [%s]",
                             right.get("terms"))
        _terms = None if right.get("terms") is None else [Term.from_dict(elem) for elem in right.get("terms")]
        _channel = None if right.get("channel") is None else str(right.get("channel"))
        return Right(_channel, _terms)


@dataclass
class ResultAsset:
    content_id: str
    access_channel: str | None
    assets: List[Asset] | None

    @staticmethod
    def from_dict(result: Any) -> 'ResultAsset':
        if result.get("contentId") is None or result.get("contentId") == "":
            raise ValueError("From Assertions content_id is required:\nData [%s]", result.get("contentId"))
        _content_id = str(result.get("contentId"))
        _access_channel = None if result.get("accessChannel") is None else str(result.get("accessChannel"))
        _assets = None if result.get("assets") is None else [Asset.from_dict(elem) for elem in result.get("assets")]
        return ResultAsset(_content_id, _access_channel, _assets)


@dataclass
class ResultRights:
    content_id: str
    access_channel: str | None
    localizable_information: List[LocalizableInformation] | None
    rights: Right | None

    @staticmethod
    def from_dict(result: Any) -> 'ResultRights':
        if result.get("contentId") is None or result.get("contentId") == "":
            raise ValueError("From Assertions content_id is required:\nData [%s]", result.get("contentId"))
        _content_id = str(result.get("contentId"))

        _access_channel = None if result.get("accessChannel") is None else str(result.get("accessChannel"))
        _localizable_information = None if result.get("localizableInformation") is None else \
            [LocalizableInformation.from_dict(elem) for elem in result.get("localizableInformation")]
        _rights = None if result.get("rights") is None else Right.from_dict(result.get("rights"))
        return ResultRights(_content_id, _access_channel, _localizable_information, _rights)

    def print_title_name_medium(self):
        if (self.localizable_information is None or self.localizable_information.__len__() == 0
                or self.localizable_information[0].title_name_medium is None
                or self.localizable_information[0].title_name_medium == ''):
            logging.warning("No information available")
        else:
            logging.info(self.localizable_information[0].title_name_medium)


@dataclass
class Response:
    results: List[ResultRights] | List[ResultAsset] | None

    @staticmethod
    def from_dict(response: Any, result_type: ResultType) -> 'Response':
        match result_type:
            case ResultType.ASSET:
                _results = None if response.get("results") is None else [ResultAsset.from_dict(elem) for elem in
                                                                         response.get("results")]
                return Response(_results)
            case ResultType.RIGHT:
                _results = None if response.get("results") is None else [ResultRights.from_dict(elem) for elem in
                                                                         response.get("results")]
                return Response(_results)


def print_title_name_medium(result_right: List[ResultRights], header: str = None):
    """
    Print TV Shows or Movies title, print also a header if present

    :param header: header description (optional)
    :param result_right: list of Right
    """
    if header is not None:
        logging.info(header)
    for result in (result_right or []):
        result.print_title_name_medium()


def print_endpoints(endpoints: List[Endpoint], header: str = None):
    """
    Print TV Shows or Movies title, print also a header if present

    :param header: header description (optional)
    :param endpoints: list of Endpoint
    """
    if header is not None:
        logging.info(header)
    for endpoint in (endpoints or []):
        endpoint.print_path()


def filter_result_by_active_data_and_video_format_and_endpoint_origin_level(result_asset: List[ResultAsset],
                                                                            contend_ids: List[str]) -> 'List[Endpoint]':
    """
    Return a list of endpoints starting from a list of ResultAsset filtered by content_id and then collecting only the
    endpoints that has video_format = "HD" and origin = "level3"

    :param result_asset: list of ResultAsset
    :param contend_ids: list of str representing content_id
    :returns List[Endpoint]: list of Endpoint
    """
    active_data: List[ResultAsset] = [result for result in (result_asset or []) if
                                      contend_ids.__contains__(result.content_id)]
    endpoints = []
    for result in active_data:
        for asset in (result.assets or []):
            if asset.is_video_format_HD_and_origin_level3():
                endpoints.append(asset.endpoints[0])
    return endpoints


def filter_result_by_active(result_rights: List[ResultRights]) -> 'List[ResultRights]':
    """
    Return a list of ResultRight that are active, that means that present current date between start_date and end_date
    of Term

    :param result_rights: list of ResultRight
    :returns List[ResultRights]: list of ResultRights
    """
    return [result for result in (result_rights or []) if result.rights.terms[0].is_active()]


def filter_result_by_can_be_played_on_ROKU(result_rights: List[ResultRights]) -> 'List[ResultRights]':
    """
    Return a list of ResultRight that can be played by ROKU, that means that in TERM data there is a device with
    device_platform equals to ROKU

    :param result_rights: list of ResultAsset
    :returns List[ResultRights]: list of ResultRights
    """
    return [result for result in (result_rights or []) if result.rights.terms[0].can_be_played_on_ROKU()]
