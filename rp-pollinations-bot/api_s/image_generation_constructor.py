import logging as log
import random as rnd
import json
import os
from typing import Optional
from together import Together
import asyncio
from concurrent.futures import ThreadPoolExecutor

class BrokenFileError(Exception):
    pass

class InvalidParamsError(Exception):
    pass

class ImageGenerationConstructor:
    def __init__(
        self,
        seed: Optional[int] = None,
        schema_path: str = './api_s/params_img_gen.json',
        model: Optional[str] = None
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

        self.api_key: Optional[str] = None 
        self.model: str = model or schema.get("model", "black-forest-labs/FLUX.1-pro")
        self.width: int = schema.get("width", 1024)
        self.height: int = schema.get("height", 1024)
        self.steps: int = schema.get("steps", 30)
        self.default_seed: int = seed if seed is not None else rnd.randint(0, 100_000_000)
        self._prompt: str = ""
        self._client: Optional[Together] = None

    async def __aenter__(self):
        # get api key
        if self.api_key is None:
            self.api_key = await self.fetch_api_key()
        if self._client is None:
            self._client = Together(api_key=self.api_key)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass  # no session to close

    async def fetch_api_key(self):
        import aiohttp
        url = "https://www.codegeneration.ai/activate-v2"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    log.critical(f"Can't fetch API key: {response.status}")
                    raise InvalidParamsError(f"Failed to get API key: {response.status}")
                data = await response.json()
                api_key = data.get("openAIParams", {}).get("apiKey")
                if not api_key:
                    raise InvalidParamsError("API key not found in response!")
                log.info("Got Together.ai API key automatically.")
                return api_key

    def validate_all(self) -> None:
        correct_params: dict = {
            'model': str,
            'width': int,
            'height': int,
            'default_seed': int,
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

    def url_constructor(self, *a, **k) -> str:
        log.warning("url_constructor is not supported for TogetherAI SDK (use generate_image)")
        return "https://api.together.xyz/v1/images/generate"

    async def generate_image(self, prompt: Optional[str] = None, seed: Optional[int] = None, return_base64: bool = False):
        if prompt is not None:
            self.set_prompt(prompt)
        if not self._prompt:
            log.error("Prompt is not set or is empty.")
            raise InvalidParamsError("Prompt must be set before generating image.")

        if self._client is None:
            raise RuntimeError("Together SDK client not initialized (use async with).")

        payload = {
            "prompt": self._prompt,
            "model": self.model,
            "width": self.width,
            "height": self.height,
            "steps": self.steps,
            "disable_safety_checker": True,
        }
        if seed is not None:
            payload["seed"] = seed
        else:
            payload["seed"] = self.default_seed

        loop = asyncio.get_running_loop()
        # together.images.generate() is sync, so run it in executor
        def do_gen():
            resp = self._client.images.generate(**payload)
            data = resp.data[0]
            if return_base64 and hasattr(data, "base64"):
                log.info(f"Image (base64) generated successfully.")
                return data.base64
            elif hasattr(data, "url"):
                log.info(f"Image (url) generated successfully: {data.url}")
                return data.url
            else:
                log.error(f"No valid image url/base64 in response: {data}")
                return None

        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, do_gen)
        return result
