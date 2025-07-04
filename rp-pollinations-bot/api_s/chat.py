from api_s.chat_request_constructor import ChatRequestConstructor, Roles
import openai as ai


class Chat:
    def __init__(self, base_api_url: str = 'https://text.pollinations.ai/openai', api_key: str = '',
                 model: str = '', main_prompt: str = '', stream: bool = True, max_tokens: int = 4096):
        self.cr_constructor = ChatRequestConstructor(model, stream = stream, max_tokens=max_tokens)
        if main_prompt != '':
            self.cr_constructor.add_message(Roles.SYSTEM, main_prompt)
        self.client = ai.AsyncOpenAI(base_url=base_api_url, api_key=api_key)

    async def make_gpt_request(self) -> str | ai.AsyncStream:
        config = self.cr_constructor.generate_config()
        generated = True
        for i in range(10):
            try:
                response = await self.client.chat.completions.create(**config)
            except Exception as e:
                generated = False
            if generated:
                break
        if self.cr_constructor.stream:
            return response
        content = response.choices[0].message.content
        sponsor_marker = "**Sponsor**"
        idx = content.find(sponsor_marker)
        if idx != -1:
            content = content[:idx].rstrip()
        return content

    def add_user_message(self, content: str) -> None:
        self.cr_constructor.add_message(Roles.USER, content)

    def add_system_message(self, content: str) -> None:
        self.cr_constructor.add_message(Roles.SYSTEM, content)

    def add_assistant_message(self, content: str) -> None:
        self.cr_constructor.add_message(Roles.ASSISTANT, content)

    def remove_message(self, mid: int) -> None:
        self.cr_constructor.remove_message(mid)

    def change_role(self, mid: int, role: Roles) -> None:
        self.cr_constructor.change_role(mid, role)

    def change_content(self, mid: int, content: str) -> None:
        self.cr_constructor.change_content(mid, content)