import os
from typing import IO

from azure.storage.blob import BlobServiceClient


def get_container_client():
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_client_ = blob_service_client.get_container_client(container="quran-app")
    return container_client_


container_client = get_container_client()


def upload_file(filename: str, file: IO) -> str:
    blob_client = container_client.upload_blob(name=filename, data=file, overwrite=True)
    return blob_client.url
