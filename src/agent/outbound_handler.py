class OutboundHandler:
    def __init__(self, caller_id: str):
        self.caller_id = caller_id
        self.context = {"caller_id": caller_id, "official_data": {}}

    async def generate_prompt(self) -> str:
        return "السلام عليكم، نتصل بكم من حكومة دبي بخصوص المعاملة الخاصة بكم."
