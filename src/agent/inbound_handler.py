class InboundHandler:
    def __init__(self, caller_id: str):
        self.caller_id = caller_id
        self.context = {"caller_id": caller_id, "official_data": {}}

    async def handle_query(self, query: str) -> str:
        return f"مرحباً بك في مركز الاتصال الحكومي بدبي. بخصوص استفسارك عن {query}، تفضل بالسؤال وسنقوم بخدمتك وفق الأنظمة الرسمية."

    async def generate_prompt(self) -> str:
        return "مرحباً بك، كيف أستطيع مساعدتك اليوم؟"
