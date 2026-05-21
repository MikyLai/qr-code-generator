import os
from datetime import datetime, timedelta

from azure.storage.blob import BlobSasPermissions, BlobServiceClient, ContentSettings, generate_blob_sas

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

# Override the host:port used in public-facing blob URLs (e.g. browser redirects).
# Useful when the internal Docker hostname (e.g. "azurite") differs from what the
# browser can reach (e.g. "localhost").
BLOB_PUBLIC_HOST = os.getenv("BLOB_PUBLIC_HOST", "")


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


def generate_sas_url(token: str, expiry_hours: int = 24) -> str:
    """產生指定 token QR Code 圖片的 SAS URL，預設有效期 24 小時。"""
    client = _get_service_client()
    account_key = client.credential.account_key
    sas_token = generate_blob_sas(
        account_name=client.account_name,
        container_name=CONTAINER_NAME,
        blob_name=f"{token}.png",
        account_key=account_key,
        permission=BlobSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=expiry_hours),
    )
    blob_client = client.get_blob_client(container=CONTAINER_NAME, blob=f"{token}.png")
    url = f"{blob_client.url}?{sas_token}"
    if BLOB_PUBLIC_HOST:
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        url = urlunparse(parsed._replace(netloc=BLOB_PUBLIC_HOST))
    return url
