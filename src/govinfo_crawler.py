import datetime
import json
import logging
import os
import time
from typing import Dict
from urllib.parse import quote
from zoneinfo import ZoneInfo

import regex
import requests

import settings

API_KEY = settings.GOVINFO_KEY


def __create_data_dir() -> None:
    """create data directory if not exists."""
    folder_path = f"{os.path.dirname(__file__)}/../data"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logging.info(f"フォルダ'{folder_path}'を作成しました。")
    else:
        logging.info(f"フォルダ'{folder_path}'は既に存在します。")


def __export_json_file(file_name: str, data: Dict[str, str | int]) -> None:
    """export json file.

    Args:
        file_name (str): file name.
        data (Dict[str, str | int]): export data.
    """
    with open(f"{os.path.dirname(__file__)}/../data/{file_name}.json", "w") as f:
        json.dump(data, f, indent=2)


def crawling_bill_collections(start_date: str) -> Dict[str, str | int]:
    """crawling bill collections from govinfo api.

    Args:
        start_date (str): collection start date. format: 'YYYY-MM-DDTHH:MM:SSZ'

    Raises:
        ValueError: error date syntax.

    Returns:
        Dict[str, str | int]: crawling result.
    """
    if regex.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", start_date):
        size = 1000
        file_date = start_date.split("T")[0]
        __create_data_dir()
        encoded_start_date = quote(start_date)
        res = requests.get(
            f"https://api.govinfo.gov/collections/BILLS/{encoded_start_date}?pageSize={size}&offsetMark=%2A&api_key={API_KEY}"
        )
        bill_data = res.json()
        __export_json_file(f"{file_date}_export_bills_0", bill_data)
        i = 1
        # 1000件以上の場合は、次ページがあるか確認して取得
        while bill_data["nextPage"]:
            logging.info(f"{i=}")
            time.sleep(1)
            res = requests.get(f"{bill_data['nextPage']}&api_key={API_KEY}")
            bill_data = res.json()
            __export_json_file(f"{file_date}_export_bills_{i}", bill_data)
            i += 1
    else:
        raise ValueError(f"error date syntax: '{start_date}'.")

    return {"code": 200, "message": "success"}


if __name__ == "__main__":
    # now = datetime.datetime.now(ZoneInfo("Asia/Tokyo"))
    now = datetime.datetime(2025, 1, 1, tzinfo=ZoneInfo("Asia/Tokyo"))
    message = crawling_bill_collections(now.strftime("%Y-%m-%dT%H:%M:%SZ"))
