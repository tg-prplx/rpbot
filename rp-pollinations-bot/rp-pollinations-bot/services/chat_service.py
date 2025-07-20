from ast import Not
from api_s.chat import Chat
from api_s.image_generation_constructor import ImageGenerationConstructor
import logging as log
from typing import Optional
import re

class NotSupportedError: pass
class NotGeneratedError: pass

class ChatService:
    def __init__(self, *args, **kwargs):
        self.chat = Chat(*args, **kwargs)

    async def handle_message(self, message_content: str) -> tuple[str, Optional[str]]:
        self.chat.add_user_message(message_content)
        if self.chat.cr_constructor.stream:
            log.critical('Responce stream isnt supported yet.')
            raise NotSupportedError()
        resp: str = await self.chat.make_gpt_request()
        match = re.search(r'\[(.*?)\]', resp)
        image_prompt: Optional[str] = None
        if match:
            image_prompt = match.group(1)
            self.chat.add_assistant_message(resp)
            return resp.replace(f"[{match.group(1)}]", ''), image_prompt
        return resp, image_prompt
        

    async def handle_image(self, prompt: str):
        generated: bool = False
        async with ImageGenerationConstructor() as igc:
                for i in range(3):
                    image_url = await igc.generate_image(prompt)
                    if image_url != None:
                        generated = True
                        break
                if not generated:
                    raise NotGeneratedError()
        return image_url