"""
Пример использования Azure blob storage
"""

import os
from azure.storage.blob import BlobServiceClient

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container="quran-app")

# Добавление файла
with open(file="filename", mode="rb") as data:
    blob_client = container_client.upload_blob(name="filename", data=data, overwrite=True)

# Удаление файла
blob_client = container_client.get_blob_client(blob="blob_name")
blob_client.delete_blob()

# Получение списка
blob_list = container_client.list_blobs()
for blob in blob_list:
    print(f"Name: {blob.name}")
