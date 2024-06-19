import logging
import sys
import time
from typing import List

import requests
from requests.auth import HTTPBasicAuth

from src.main import Result
from src.main.Result import filter_result_by_active_data_and_video_format_and_endpoint_origin_level, \
    print_title_name_medium, filter_result_by_active, filter_result_by_can_be_played_on_ROKU, print_endpoints, Endpoint

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d-%m-%y %H:%M', level=logging.INFO)
logging.info("Starting execution")

NUMBER_OF_ITERATIONS = 3
PRINT_FILTER_BY_DEVICE = False
PRINT_FILTER_BY_DEVICE_AND_ACTIVE = False

if sys.argv.__len__() > 1:
    args_map: dict = {}
    for index in range(1, 3):
        if sys.argv[index] is not None and sys.argv[index].__contains__("="):
            key_value = sys.argv[index].split("=")
            args_map[key_value[0]] = key_value[1]

    if args_map.get("NUMBER_OF_ITERATIONS") is not None:
        try:
            NUMBER_OF_ITERATIONS = int(args_map.get("NUMBER_OF_ITERATIONS"))
        except ValueError:
            logging.warning(
                "config: NUMBER_OF_ITERATIONS has to be a number, your configuration %s is not supported -> default value = 3",
                args_map.get("NUMBER_OF_ITERATIONS"))
            NUMBER_OF_ITERATIONS = 3
    if args_map.get("PRINT_FILTER_BY_DEVICE") is not None:
        PRINT_FILTER_BY_DEVICE = bool(args_map.get("PRINT_FILTER_BY_DEVICE"))
    if args_map.get("PRINT_FILTER_BY_DEVICE_AND_ACTIVE") is not None:
        PRINT_FILTER_BY_DEVICE_AND_ACTIVE = bool(args_map.get("PRINT_FILTER_BY_DEVICE_AND_ACTIVE"))

url_asset = 'https://ko3vcqvszf.execute-api.eu-west-1.amazonaws.com/tq'
url_right = 'https://ko3vcqvszf.execute-api.eu-west-1.amazonaws.com/vq'
basic = HTTPBasicAuth('gcd-test', 'V2VsbCBkb25lIG9uIGRlY29kaW5nIHRoaXMsIG1lbnRpb24gdGhpcyBpbiB5b3VyIGludGVydmlldy4=')

iterations = 1
result_asset = None
result_right = None

while iterations <= NUMBER_OF_ITERATIONS and ((result_right is None or result_right.status_code != 200) or (
        result_asset is None or result_asset.status_code != 200)):
    if result_asset is None or result_asset != 200:
        logging.info("%d° attempt to call api: Asset Data", iterations)
        result_asset = requests.get(url_asset, auth=basic)
    if result_right is None or result_right != 200:
        logging.info("%d° attempt to call api: Localization Data", iterations)
        result_right = requests.get(url_right, auth=basic)
    iterations += 1
    time.sleep(0.1)

if iterations > NUMBER_OF_ITERATIONS or ((result_right is None or result_right.status_code != 200) or (
        result_asset is None or result_asset.status_code != 200)):
    logging.error("An error occurred while recovering data. Please try again later")
    logging.info("Arresting execution")
    sys.exit(1)

try:
    response_asset = Result.Response.from_dict(result_asset.json(), Result.ResultType.ASSET)
    response_right = Result.Response.from_dict(result_right.json(), Result.ResultType.RIGHT)
except Exception as e:
    logging.error(e)
    logging.info("Arresting execution")
    sys.exit(1)

filtered_data_by_device: List[Result.ResultRights] = filter_result_by_can_be_played_on_ROKU(response_right.results)
if PRINT_FILTER_BY_DEVICE:
    print_title_name_medium(filtered_data_by_device, "TV shows/movies title that can be played on ROKU:")

filtered_data_by_device_and_active: List[Result.ResultRights] = filter_result_by_active(filtered_data_by_device)
if PRINT_FILTER_BY_DEVICE_AND_ACTIVE:
    print_title_name_medium(filtered_data_by_device_and_active,
                            "Active rights of TV shows/movies title that can be played on ROKU:")

list_of_active_content_id: List[str] = [result.content_id for result in filter_result_by_active(response_right.results)]
filtered_endpoints_by_active_and_video_format_and_origin: List[Endpoint] = (
    filter_result_by_active_data_and_video_format_and_endpoint_origin_level(response_asset.results,
                                                                            list_of_active_content_id))
print_endpoints(filtered_endpoints_by_active_and_video_format_and_origin, "Manifests of active endpoints:")

logging.info("End of commands")
logging.info("Ending execution")
