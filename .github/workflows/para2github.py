import json
import os
import re
from typing import Tuple

import requests


# 从环境变量中获取必要的Token和项目ID
token: str = os.environ["API_TOKEN"]
gittoken: str = os.environ["GH_TOKEN"]
project_id: str = os.environ["PROJECT_ID"]
file_url: str = f"https://paratranz.cn/api/projects/{project_id}/files/"

# 初始化列表和字典
file_id_list: list[int] = []
file_path_list: list[str] = []
zh_cn_list: list[dict[str, str]] = []


def translate(file_id: int) -> Tuple[list[str], list[str]]:
    """
    获取指定文件的翻译内容并返回键值对列表。

    :param file_id: 文件ID
    :return: 包含键和值的元组列表
    """
    url: str = (
        f"https://paratranz.cn/api/projects/{project_id}/files/{file_id}/translation"
    )
    response: requests.Response = requests.get(
        url, headers={"Authorization": token, "accept": "*/*"}
    )
    translations: list[dict[str, str]] = response.json()

    keys: list[str] = []
    values: list[str] = []

    for item in translations:
        keys.append(item["key"])
        translation: str = item["translation"]
        original: str = item["original"]
        values.append(
            original
            if not translation and (item["stage"] == 0 or item["stage"] == -1)
            else translation
        )

    return keys, values


def get_files() -> None:
    """
    获取项目中的文件列表并提取文件ID和路径。
    """
    response: requests.Response = requests.get(
        file_url, headers={"Authorization": token, "accept": "*/*"}
    )
    files: list[dict[str, str]] = response.json()

    for file in files:
        file_id_list.append(file["id"])
        file_path_list.append(file["name"])


def save_translation(zh_cn_dict: dict[str, str], path: str) -> None:
    dir_path: str = os.path.join("CNPack", os.path.dirname(path))
    os.makedirs(dir_path, exist_ok=True)
    file_path: str = os.path.join(dir_path, "zh_cn.json")

    with open(file_path, "w+", encoding="UTF-8") as f:
        json.dump(zh_cn_dict, f, ensure_ascii=False, indent=4, separators=(",", ":"))


def main() -> None:
    get_files()

    for file_id, path in zip(file_id_list, file_path_list):
        keys, values = translate(file_id)
        zh_cn_dict: dict[str, str] = {
            key: re.sub(r"\\n", "\n", value) for key, value in zip(keys, values)
        }
        zh_cn_dict: dict[str, str] = {
            key1: re.sub(r"\\u00b7", "\u00b7", value) for key, value in zip(keys, values)
        }
        if "ftbquest" in path:
            zh_cn_dict = {
                key: (value.replace(" ", "\u00A0") if "image" not in value else value)
                for key, value in zip(keys, values)
            }
        if "TM" in path:
            continue

        zh_cn_list.append(zh_cn_dict)
        save_translation(zh_cn_dict, path)
        print(f"上传完成：{re.sub('en_us.json', 'zh_cn.json', path)}")


if __name__ == "__main__":
    main()
