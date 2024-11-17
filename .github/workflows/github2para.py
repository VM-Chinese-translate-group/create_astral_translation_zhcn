import asyncio
import os
from pathlib import Path

import paratranz_client

TOKEN: str = os.getenv("API_TOKEN", "")
PROJECT_ID: str = os.getenv("PROJECT_ID", "")

if not TOKEN or not PROJECT_ID:
    raise EnvironmentError("环境变量 API_TOKEN 或 PROJECT_ID 未设置。")

# 配置 Paratranz 客户端
configuration = paratranz_client.Configuration(host="https://paratranz.cn/api")
configuration.api_key["Token"] = TOKEN
project_id: int = int(PROJECT_ID)


async def upload_file(file_path: Path, upload_path: str) -> None:
    """异步上传文件到 Paratranz"""
    async with paratranz_client.ApiClient(configuration) as api_client:
        api_instance = paratranz_client.FilesApi(api_client)
        try:
            await api_instance.create_file(
                project_id, file=str(file_path), path=upload_path
            )
            print(f"Uploaded {file_path} successfully.")
        except Exception as e:
            print(f"Exception when uploading {file_path}: {e}")


def get_file_list(dir_path: Path) -> list[Path]:
    """获取指定目录下所有匹配的文件"""
    file_list: list[Path] = []
    if dir_path.is_file() and dir_path.suffix == ".json" and "en_us" in dir_path.name:
        file_list.append(dir_path)
    elif dir_path.is_dir():
        for item in dir_path.iterdir():
            file_list.extend(get_file_list(item))
    return file_list


async def main() -> None:
    dir_path = Path(os.environ["FILE_PATH"])
    file_list: list[Path] = get_file_list(dir_path)

    for file_path in file_list:
        relative_path: Path = file_path.relative_to("CNPack")
        upload_path: str = relative_path.parent.as_posix()

        print(f"Uploading {file_path} to {upload_path}")
        await upload_file(file_path, upload_path)


if __name__ == "__main__":
    asyncio.run(main())
