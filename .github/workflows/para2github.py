import json
import os
import re
from pathlib import Path
from typing import Tuple

import requests

TOKEN: str = os.getenv("API_TOKEN", "")
PROJECT_ID: str = os.getenv("PROJECT_ID", "")
FILE_URL: str = f"https://paratranz.cn/api/projects/{PROJECT_ID}/files/"

if not TOKEN or not PROJECT_ID:
    raise EnvironmentError("环境变量 API_TOKEN 或 PROJECT_ID 未设置。")

# 初始化列表和字典
file_id_list: list[int] = []
file_path_list: list[str] = []
zh_cn_list: list[dict[str, str]] = []


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
        # 优先使用翻译内容，缺失时根据 stage 使用原文
        values.append(
            original if not translation and item["stage"] in [0, -1] else translation
        )

    return keys, values


def get_files() -> None:
    """获取项目中的文件列表并提取文件ID和路径"""
    headers = {"Authorization": TOKEN, "accept": "*/*"}
    files = fetch_json(FILE_URL, headers)

    for file in files:
        file_id_list.append(file["id"])
        file_path_list.append(file["name"])


def save_translation(zh_cn_dict: dict[str, str], path: Path) -> None:
    """
    保存翻译内容到指定的 JSON 文件，并按键字母顺序排序

    :param zh_cn_dict: 翻译内容的字典
    :param path: 原始文件路径
    """
    # 按照字母顺序排序字典的键
    sorted_zh_cn_dict = dict(sorted(zh_cn_dict.items()))

    dir_path = Path("CNPack") / path.parent
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / "zh_cn.json"

    with open(file_path, "w", encoding="UTF-8") as f:
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

    # 替换换行符
    zh_cn_dict = {key: re.sub(r"\\n", "\n", value) for key, value in zip(keys, values)}

    # 特殊处理：ftbquest 文件
    if "ftbquest" in path.name:
        zh_cn_dict = {
            key: value.replace(" ", "\u00A0") if "image" not in value else value
            for key, value in zip(keys, values)
        }

    return zh_cn_dict


def main() -> None:
    get_files()

    for file_id, path in zip(file_id_list, file_path_list):
        if "TM" in path:  # 跳过 TM 文件
            continue

        zh_cn_dict = process_translation(file_id, Path(path))
        zh_cn_list.append(zh_cn_dict)

        save_translation(zh_cn_dict, Path(path))
        print(f"已从Patatranz下载到仓库：{re.sub('en_us.json', 'zh_cn.json', path)}")


if __name__ == "__main__":
    main()
