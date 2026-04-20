import json
from azure.storage.blob import BlobServiceClient, ContentSettings


class AzureBlobWriter:
    """Writes JSON data to an Azure Blob Storage container."""

    def __init__(self, connection_string: str, container_name: str) -> None:
        """
        Initialize the AzureBlobWriter.

        :param connection_string: Azure Storage account connection string.
        :param container_name: Name of the target blob container.
        """
        self._container_name = container_name
        self._client = BlobServiceClient.from_connection_string(connection_string)

    def write(self, blob_name: str, data: dict | list, *, overwrite: bool = True) -> str:
        """
        Serialize *data* as JSON and upload it to the configured container.

        :param blob_name: Name (path) of the blob to create or overwrite.
        :param data: JSON-serializable object (dict or list).
        :param overwrite: When True (default) an existing blob is overwritten.
        :returns: The full URL of the uploaded blob.
        :raises ValueError: If *data* is not JSON-serializable.
        :raises azure.core.exceptions.AzureError: On storage operation failure.
        """
        try:
            payload = json.dumps(data, indent=2, ensure_ascii=False)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Data is not JSON-serializable: {exc}") from exc

        blob_client = self._client.get_blob_client(
            container=self._container_name, blob=blob_name
        )
        blob_client.upload_blob(
            payload.encode("utf-8"),
            blob_type="BlockBlob",
            overwrite=overwrite,
            content_settings=ContentSettings(content_type="application/json"),
        )
        return blob_client.url
