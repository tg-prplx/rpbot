from typing import Literal
import logging as log
import tiktoken as tktk
import json
from enum import Enum

class IncorrectRole(Exception):
    pass

class IncorrectContent(Exception):
    pass

class ReachTokenLimit(Exception):
    pass

class IncorrectMessageID(Exception):
    pass

class BrokenFileError(Exception):
    pass

class InvalidSchemaTypes(Exception):
    pass

class Roles(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatRequestConstructor:
    def __init__(self, model: str, max_tokens: int = 2048, token_encoding: str = "cl100k_base", schema_path: str = './api/schema_llm.json', stream: bool = True):
        self.model: str = model
        self.max_tokens: int = max_tokens
        self.messages: list[dict[str, str]] = []
        self.__correct_roles: list[str] = ['system', 'user', 'assistant']
        self.token_encoding: str = token_encoding
        self.stream = stream
        self.current_tokens: int = 0
        try:
            with open(schema_path, 'r') as f:
                 self.schema: dict = json.load(f)
        except json.JSONDecodeError:
            log.critical("Invalid schema JSON structure.")
            raise json.JSONDecodeError()
        except (PermissionError, FileNotFoundError):
            log.critical("File not found or it has no permission to read.")
            raise BrokenFileError()

    def validate_schema(self) -> None:
        for k, v in self.schema.items():
            if not isinstance(k, str) or not isinstance(v, str):
                log.critical(f'Invalid schema {k} or {v} types.')
                raise InvalidSchemaTypes()

    def __get_content(self) -> str:
        return ''.join(msg['content'] for msg in self.messages)

    def count_tokens(self, text: str) -> int:
        encoding = tktk.get_encoding(self.token_encoding)
        return len(encoding.encode(text))
    
    def validate_role(self, role: str) -> None:
        if not (isinstance(role, str) and role in self.__correct_roles):
            log.error(f'Role: {role} is not correct type or not in correct roles.')
            raise IncorrectRole()

    def check_content_addability(self, content_tokens: int) -> None:
        if (content_tokens + self.current_tokens) > self.max_tokens:
            log.critical(f'Content tokens: {content_tokens} reaches max token limit.')
            raise ReachTokenLimit()

    def validate_content(self, content: str) -> None:
        if not (isinstance(content, str)):
            log.critical(f'This content: {content} is invalid beause of incorrect type.')
            raise IncorrectContent()

    def validate_mid(self, mid: int):
        if not isinstance(mid, int) or not (0 <= mid < len(self.messages)):
           log.critical(f'Cannot delete message with id={mid} because it out of range or not be instanse of int.')
           raise IncorrectMessageID()

    def add_message(self, role: Roles, content: str, image: bool = False) -> None:
        if not image:
             self.validate_role(role)
             self.validate_content(content)
             content_tokens: int = self.count_tokens(content)
             self.check_content_addability(content_tokens)
             self.current_tokens += content_tokens
             self.messages.append({'role': role, 'content': content})
             log.info(f'Added to messages: {role}: {content}')
        else:
            self.messages.append(content)

    def remove_message(self, mid: int) -> None:
        self.validate_mid(mid)
        self.current_tokens -= self.count_tokens(self.messages[mid]['content'])
        del self.messages[mid]

    def change_role(self, mid: int, role: Roles) -> None:
        self.validate_role(role)
        self.validate_mid(mid)
        self.messages[mid]['role'] = role
        
    def change_content(self, mid: int, content: str) -> None:
        self.validate_mid(mid)
        self.validate_content(content)
        c_current_tokens: int = self.current_tokens
        self.current_tokens = self.current_tokens - self.count_tokens(self.messages[mid]['content'])
        cc_tokens: int = self.count_tokens(content)
        self.check_content_addability(cc_tokens)
        self.current_tokens += cc_tokens
        self.messages[mid]['content'] = content

    def generate_config(self) -> dict:
        self.validate_schema()
        return {
                self.schema['model']: self.model,
                self.schema['messages']: self.messages,
                self.schema['max_tokens']: self.max_tokens,
                self.schema['stream']: self.stream
            }