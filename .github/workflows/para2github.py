import json
import os
import re
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Tuple

import requests

TOKEN = os.getenv("API_TOKEN", "")
PROJECT_ID = os.getenv("PROJECT_ID", "")
FILE_URL = f"https://paratranz.cn/api/projects/{PROJECT_ID}/files/"

if len(TOKEN) != 32 or not PROJECT_ID.isdigit():
    raise EnvironmentError("未设置有效的 API_TOKEN 或 PROJECT_ID 环境变量")


def fetch_json(url: str, headers: dict[str, str]) -> list[dict[str, str]]:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def translate(file_id: int) -> Tuple[list[str], list[str]]:
    """获取指定文件的翻译内容并返回键值对列表"""
    url = f"https://paratranz.cn/api/projects/{PROJECT_ID}/files/{file_id}/translation"
    headers = {"Authorization": TOKEN, "accept": "*/*"}
    translations = fetch_json(url, headers)

    keys, values = [], []
    for item in translations:
        keys.append(item["key"])
        translation = item.get("translation", "")
        original = item.get("original", "")
        values.append(
            original if not translation and item["stage"] in [0, -1] else translation
        )

    return keys, values


def get_files() -> list[Tuple[int, str]]:
    """获取项目中的文件列表并提取文件ID和路径"""
    headers = {"Authorization": TOKEN, "accept": "*/*"}
    files = fetch_json(FILE_URL, headers)
    return [(file["id"], file["name"]) for file in files]


def save_translation(zh_cn_dict: dict[str, str], path: Path) -> None:
    """
    保存翻译内容到指定的 JSON 文件，并根据 en_us.json 的 key 顺序排序
    :param zh_cn_dict: 翻译内容的字典
    :param path: 原始文件路径
    """
    dir_path = Path("CNPack") / path.parent
    dir_path.mkdir(parents=True, exist_ok=True)

    en_us_path = dir_path / "en_us.json"
    if en_us_path.exists():
        with open(en_us_path, "r", encoding="UTF-8") as en_file:
            en_us_dict = json.load(en_file, object_pairs_hook=OrderedDict)

        # 保证 zh_cn_dict 按照 en_us_dict 的顺序排列，同时在缺少翻译时使用原文
        sorted_zh_cn_dict = OrderedDict()

        for key in en_us_dict.keys():
            if key in zh_cn_dict:
                sorted_zh_cn_dict[key] = zh_cn_dict[key]
            else:
                # 如果在 zh_cn_dict 中没有该键，使用英文原文
                sorted_zh_cn_dict[key] = en_us_dict[key]
    else:
        # 如果没有 en_us.json 文件，就直接使用 zh_cn_dict
        sorted_zh_cn_dict = OrderedDict(zh_cn_dict)

    with open(dir_path / "zh_cn.json", "w", encoding="UTF-8") as f:
        json.dump(
            sorted_zh_cn_dict, f, ensure_ascii=False, indent=4, separators=(",", ":")
        )


def process_translation(file_id: int, path: Path) -> dict[str, str]:
    """
    处理单个文件的翻译，返回翻译字典
    :param file_id: 文件ID
    :param path: 文件路径
    :return: 翻译内容字典
    """
    keys, values = translate(file_id)
    zh_cn_dict = {key: re.sub(r"\\n", "\n", value) for key, value in zip(keys, values)}

    if "ftbquest" in path.name:
        zh_cn_dict = {
            key: value.replace(" ", "\u00A0") if "image" not in value else value
            for key, value in zip(keys, values)
        }

    return zh_cn_dict


def main() -> None:
    if sys.version_info < (3, 9):
        raise EnvironmentError("请使用 Python 3.9 及更高版本")

    for file_id, path in get_files():
        if "TM" in path:  # 机械动力：星辰专用
            continue

        zh_cn_dict = process_translation(file_id, Path(path))
        save_translation(zh_cn_dict, Path(path))
        print(f"已从Patatranz下载到仓库：{re.sub('en_us.json', 'zh_cn.json', path)}")


if __name__ == "__main__":
    main()
