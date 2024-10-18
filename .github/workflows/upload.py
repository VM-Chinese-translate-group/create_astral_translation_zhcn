import asyncio
import os
import re
from pprint import pprint
import paratranz_client

# 配置Paratranz客户端
configuration = paratranz_client.Configuration(host="https://paratranz.cn/api")
configuration.api_key['Token'] = os.environ["API_TOKEN"]
project_id = int(os.environ["PROJECT_ID"])


async def upload_file(file_path, upload_path):
    """
    异步上传文件到Paratranz。
    :param file_path: 本地文件路径
    :param upload_path: 服务器端路径
    """
    async with paratranz_client.ApiClient(configuration) as api_client:
        api_instance = paratranz_client.FilesApi(api_client)
        try:
            # 上传文件
            api_response = await api_instance.create_file(project_id, file=file_path, path=upload_path)
            print("The response of FilesApi->create_file:\n")
            pprint(api_response)
        except Exception as e:
            print(f"Exception when calling FilesApi->create_file: {e}\n")


def get_filelist(dir_path, file_list):
    """
    获取指定目录下所有符合条件的文件。
    :param dir_path: 目录路径
    :param file_list: 文件列表
    :return: 更新后的文件列表
    """
    if os.path.isfile(dir_path):
        if re.match(".+(en_us.json)$", dir_path):
            file_list.append(dir_path)
        # # 若只是要返回文件名，使用这个
        # file_list.append(os.path.basename(dir_path))
    elif os.path.isdir(dir_path):
        for item in os.listdir(dir_path):
            # # 如果需要忽略某些文件夹，使用以下代码
            # if item == "xxx":
            #     continue
            # if item == "patchouli_books":
            #     continue
            new_path = os.path.join(dir_path, item)
            get_filelist(new_path, file_list)
    return file_list


async def main():
    file_list = get_filelist(os.environ["FILE_PATH"], [])

    for file_path in file_list:
        relative_path = file_path.split("CNPack")[1]
        upload_path = relative_path.replace('\\', '/').replace(os.path.basename(file_path), "")
        print(f"Uploading {file_path} to {upload_path}\n")
        await upload_file(file_path, upload_path)


if __name__ == '__main__':
    asyncio.run(main())