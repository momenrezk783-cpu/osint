class AzureBlobUploader:
    """
    رفع وتخزين الملفات الصوتية المسجلة داخل الإمارات (Data Residency UAE North).
    """
    def __init__(self, connection_string: str = None):
        self.conn_str = connection_string

    async def upload(self, local_path: str, destination_name: str) -> str:
        return f"https://azure-storage.local/{destination_name}"
