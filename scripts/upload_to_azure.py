import asyncio
import glob
from config.settings import settings
from src.integrations.azure_blob import AzureBlobUploader

async def main():
    uploader = AzureBlobUploader(settings.azure_storage_connection_string)
    for file in glob.glob("assets/*.mp3"):
        print(f"Uploading {file} to Azure Blob Storage...")
        await uploader.upload(file, file)

if __name__ == "__main__":
    asyncio.run(main())
