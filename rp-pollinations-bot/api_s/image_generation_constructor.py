from typing import Optional
import urllib.parse as parse
import logging as log
import random as rnd
import json
import aiohttp

class BrokenFileError(Exception):
    pass

class InvalidParamsError(Exception):
    pass

class ImageGenerationConstructor:
    def __init__(
        self, 
        seed: Optional[int] = None, 
        endpoint: str = 'https://image.pollinations.ai/prompt/', 
        schema_path: str = './api_s/params_img_gen.json'
    ):
        try:
            with open(schema_path, 'r') as f:
                schema: dict = json.load(f)
        except json.JSONDecodeError:
            log.critical("Invalid params JSON structure.")
            raise BrokenFileError("Invalid JSON schema structure!")
        except (PermissionError, FileNotFoundError):
            log.critical("File not found or no read permission.")
            raise BrokenFileError("No access or file does not exist!")

        self.model: str = schema.get("model", "turbo")
        self.width: int = schema.get("width", 512)
        self.height: int = schema.get("height", 512)
        self.default_seed: int = seed if seed is not None else rnd.randint(0, 100_000_000)
        self.nologo: bool = bool(schema.get("nologo", True))
        self.enhance: bool = bool(schema.get("enhance", True))
        self.endpoint: str = endpoint
        self._prompt: str = ""
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()
            log.info("aiohttp session started.")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._session:
            await self._session.close()
            self._session = None
            log.info("aiohttp session closed.")

    async def generate_image(self, prompt: Optional[str] = None, seed: Optional[int] = None):
        if prompt is not None:
            self.set_prompt(prompt)
        if not self._prompt:
            log.error("Prompt is not set or is empty.")
            raise InvalidParamsError("Prompt must be set before generating image.")

        seed_to_use = seed if seed is not None else self.default_seed
        url = self.url_constructor(seed=seed_to_use)

        if not self._session:
            log.error("aiohttp session is not initialized. Use 'async with' to manage session.")
            raise RuntimeError("aiohttp session is not initialized.")

        async with self._session.get(url) as response:
            if response.status == 200:
                log.info(f"Image generated successfully: {url}")
                image_bytes = await response.read()
                return url
            else:
                text = await response.text()
                log.error(f"Failed to generate image: {response.status} {text}")
                return None

    def validate_all(self) -> None:
        correct_params: dict = {
            'model': str,
            'width': int,
            'height': int,
            'default_seed': int,
            'nologo': bool,
            'enhance': bool,
            '_prompt': str
        }
        for key, expected_type in correct_params.items():
            value = getattr(self, key)
            if not isinstance(value, expected_type):
                log.error(f"Parameter '{key}' = {value} (type={type(value)}) does not match {expected_type}")
                raise InvalidParamsError(
                    f"{key} must be of type {expected_type.__name__}, not {type(value).__name__} (actual value: {value})"
                )
        log.info("Image generation parameters are valid.")

    def url_constructor(self, seed: Optional[int] = None) -> str:
        self.validate_all()
        if not self._prompt:
            log.warning("Empty prompt when constructing URL!")
        prompt_encoded = parse.quote(self._prompt)
        actual_seed = seed if seed is not None else self.default_seed
        url = (
            f"{self.endpoint}{prompt_encoded}"
            f"?model={self.model}&width={self.width}&height={self.height}"
            f"&seed={actual_seed}&referer=http://pollinations.ai&nologo={str(self.nologo).lower()}&enhance={str(self.enhance).lower()}"
        )
        log.info(f"Constructed URL: {url}")
        return url

    def set_prompt(self, prompt: str) -> None:
        if not isinstance(prompt, str):
            log.error("Prompt must be a string.")
            raise InvalidParamsError("Prompt must be a string!")
        stripped = prompt.strip()
        if not stripped:
            log.error("Prompt is empty after stripping.")
            raise InvalidParamsError("Prompt cannot be empty!")
        self._prompt = stripped
        log.info(f"Prompt set: {self._prompt!r}")

    def get_prompt(self) -> str:
        return self._prompt