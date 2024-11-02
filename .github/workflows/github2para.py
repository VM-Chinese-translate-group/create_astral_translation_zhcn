import asyncio
import os
import re
import paratranz_client

# 配置 Paratranz 客户端
configuration = paratranz_client.Configuration(host="https://paratranz.cn/api")
configuration.api_key["Token"] = os.environ["API_TOKEN"]
project_id: int = int(os.environ["PROJECT_ID"])


async def upload_file(file_path: str, upload_path: str) -> None:
    """异步上传文件到 Paratranz"""
    async with paratranz_client.ApiClient(configuration) as api_client:
        api_instance = paratranz_client.FilesApi(api_client)
        try:
            await api_instance.create_file(project_id, file=file_path, path=upload_path)
            print(f"Uploaded {file_path} successfully.")
        except Exception as e:
            print(f"Exception when uploading files: {e}")


def get_file_list(dir_path: str) -> list[str]:
    """获取指定目录下所有匹配的文件"""
    file_list: list[str] = []
    if os.path.isfile(dir_path):
        if re.match(r".+\.en_us\.json$", dir_path):
            file_list.append(dir_path)
    elif os.path.isdir(dir_path):
        for item in os.listdir(dir_path):
            new_path = os.path.join(dir_path, item)
            file_list.extend(get_file_list(new_path))
    return file_list


async def main() -> None:
    file_list: list[str] = get_file_list(os.environ["FILE_PATH"])

    for file_path in file_list:
        relative_path: str = file_path.split("CNPack")[1]
        upload_path: str = relative_path.replace("\\", "/").replace(
            os.path.basename(file_path), ""
        )
        print(f"Uploading {file_path} to {upload_path}")
        await upload_file(file_path, upload_path)


if __name__ == "__main__":
    asyncio.run(main())
