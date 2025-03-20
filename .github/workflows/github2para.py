import asyncio
import os
import json
from pprint import pprint
import paratranz_client
from pydantic import ValidationError

configuration = paratranz_client.Configuration(host="https://paratranz.cn/api")
configuration.api_key["Token"] = os.environ["API_TOKEN"]


async def upload_file(path, file):
    async with paratranz_client.ApiClient(configuration) as api_client:
        api_instance = paratranz_client.FilesApi(api_client)
        project_id = int(os.environ["PROJECT_ID"])
        files_response = await api_instance.get_files(project_id)
        try:
            # 第一次创建文件
            api_response = await api_instance.create_file(
                project_id, file=file, path=path
            )
            pprint(api_response)
        except ValidationError as error:
            print(f"文件上传成功{path}en_us.json")
        except Exception as e:
            filePath: str = json.loads(e.__dict__.get("body"))["message"].split(" ")[1]
            for fileName in files_response:
                if fileName.name == filePath:
                    await api_instance.update_file(project_id, file_id=fileName.id, file=file)
                    print(f"文件已更新！文件路径为：{fileName.name}")


def get_filelist(dir):
    filelist = []
    for root, _, files in os.walk(dir):
        for file in files:
            if "en_us" in file and file.endswith(".json"):
                filelist.append(os.path.join(root, file))
    return filelist


async def main():
    files = get_filelist("./Source")
    tasks = []

    for file in files:
        path = (
            file.split("Source")[1]
            .replace("\\", "/")
            .replace(os.path.basename(file), "")
        )
        print(f"Uploading {file} to {path}")
        tasks.append(upload_file(path=path, file=file))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
