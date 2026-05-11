import os

from azure.storage.blob import BlobServiceClient, ContentSettings

# Azurite local default connection string (used when env var not set)
# "UseDevelopmentStorage=true" is the official shorthand for Azurite
_AZURITE_CONNECTION_STRING = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)

AZURE_STORAGE_CONNECTION_STRING = os.getenv(
    "AZURE_STORAGE_CONNECTION_STRING",
    _AZURITE_CONNECTION_STRING,
)
CONTAINER_NAME = os.getenv("AZURE_BLOB_CONTAINER", "qr-codes")


def _get_service_client() -> BlobServiceClient:
    return BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)


def ensure_container() -> None:
    """建立 container（若已存在則略過），設定 blob 層級公開讀取。"""
    client = _get_service_client()
    container_client = client.get_container_client(CONTAINER_NAME)
    try:
        container_client.create_container(public_access="blob")
    except Exception:
        pass  # Container already exists


def upload_qr_png(token: str, png_bytes: bytes) -> str:
    """上傳 QR Code PNG 至 Blob Storage，回傳 blob URL。"""
    client = _get_service_client()
    blob_client = client.get_blob_client(container=CONTAINER_NAME, blob=f"{token}.png")
    blob_client.upload_blob(
        png_bytes,
        overwrite=True,
        content_settings=ContentSettings(content_type="image/png"),
    )
    return blob_client.url


def get_blob_url(token: str) -> str:
    """回傳指定 token 的 blob 公開 URL（不驗證是否存在）。"""
    client = _get_service_client()
    blob_client = client.get_blob_client(container=CONTAINER_NAME, blob=f"{token}.png")
    return blob_client.url
