import asyncio
import os
import sys
from pathlib import Path

import paratranz_client

TOKEN = os.getenv("API_TOKEN", "")
PROJECT_ID = os.getenv("PROJECT_ID", "")

if len(TOKEN) != 32 or not PROJECT_ID.isdigit():
    raise EnvironmentError("未设置有效的 API_TOKEN 或 PROJECT_ID 环境变量")

# 配置 Paratranz 客户端
configuration = paratranz_client.Configuration(host="https://paratranz.cn/api")
configuration.api_key["Token"] = TOKEN
PROJECT_ID = int(PROJECT_ID)


async def upload_file(file_path: Path, upload_path: str) -> None:
    """异步上传文件到 Paratranz"""
    async with paratranz_client.ApiClient(configuration) as api_client:
        api_instance = paratranz_client.FilesApi(api_client)
        try:
            await api_instance.create_file(
                PROJECT_ID, file=str(file_path), path=upload_path
            )
            print(f"Uploaded {file_path} successfully.")
        except Exception as e:
            print(f"Exception when uploading {file_path}: {e}")


def get_file_list(dir_path: Path) -> list[Path]:
    """获取指定目录下所有匹配的文件"""
    file_list = []
    if dir_path.is_file() and dir_path.suffix == ".json" and "en_us" in dir_path.name:
        file_list.append(dir_path)
    elif dir_path.is_dir():
        for item in dir_path.iterdir():
            file_list.extend(get_file_list(item))
    return file_list


async def main() -> None:
    if sys.version_info < (3, 9):
        raise EnvironmentError("请使用 Python 3.9 及更高版本")

    dir_path = Path(os.environ["FILE_PATH"])
    file_list = get_file_list(dir_path)

    for file_path in file_list:
        relative_path = file_path.relative_to("CNPack")
        upload_path = relative_path.parent.as_posix()

        print(f"Uploading {file_path} to {upload_path}")
        await upload_file(file_path, upload_path)


if __name__ == "__main__":
    asyncio.run(main())
