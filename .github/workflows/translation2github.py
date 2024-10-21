import json
import os
import re
from typing import List, Dict, Tuple

import requests

# 从环境变量中获取必要的Token和项目ID
token = os.environ["API_TOKEN"]
gittoken = os.environ["GH_TOKEN"]
project_id = os.environ["PROJECT_ID"]
file_url = f"https://paratranz.cn/api/projects/{project_id}/files/"

# 初始化列表和字典
file_id_list: List[int] = []
file_path_list: List[str] = []
zh_cn_list: List[Dict[str, str]] = []


def translate(file_id: int) -> Tuple[List[str], List[str]]:
    """
    获取指定文件的翻译内容并返回键值对列表。

    :param file_id: 文件ID
    :return: 包含键和值的元组列表
    """
    url = f"https://paratranz.cn/api/projects/{project_id}/files/{file_id}/translation"
    response = requests.get(url, headers={"Authorization": token, "accept": "*/*"})
    translations = response.json()
    keys, values = [], []

    for item in translations:
        keys.append(item["key"])
        translation = item["translation"]
        original = item["original"]
        values.append(original if not translation and (item["stage"] == 0 or item["stage"] == -1) else translation)

    return keys, values


def get_files() -> None:
    """
    获取项目中的文件列表并提取文件ID和路径。
    """
    response = requests.get(file_url, headers={"Authorization": token, "accept": "*/*"})
    files = response.json()

    for file in files:
        file_id_list.append(file["id"])
        file_path_list.append(file["name"])


def save_translation(zh_cn_dict: Dict[str, str], path: str) -> None:
    """
    保存翻译字典为JSON文件。

    :param zh_cn_dict: 翻译字典
    :param path: 文件路径
    """
    dir_path = os.path.join("CNPack", os.path.dirname(path))
    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, "zh_cn.json")

    with open(file_path, "w+", encoding='UTF-8') as f:
        json.dump(zh_cn_dict, f, ensure_ascii=False, indent=4, separators=(',', ':'))


def main() -> None:
    get_files()

    for file_id, path in zip(file_id_list, file_path_list):
        keys, values = translate(file_id)
        zh_cn_dict = {key: re.sub(r'\\n', '\n', value) for key, value in zip(keys, values)}
        if "ftbquest" in path:
            zh_cn_dict = {key: (str.replace(value," ","\u00A0") if "image" not in value else value) for key, value in zip(keys, values)}
        if "TM" in path:
            continue;
        zh_cn_list.append(zh_cn_dict)
        save_translation(zh_cn_dict, path)
        print(f"上传完成：{re.sub('en_us.json','zh_cn.json',path)}")


if __name__ == '__main__':
    main()
