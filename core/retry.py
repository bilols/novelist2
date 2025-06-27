# v2025‑07‑02‑AI-generated
"""
core.retry – decorator to retry a function up to N times when it raises
openai.OpenAIError or jsonschema.ValidationError.
"""
from functools import wraps
import time
from typing import Callable, Type
import openai, jsonschema

RETRY_EXC: tuple[Type[Exception], ...] = (
    openai.OpenAIError,
    jsonschema.ValidationError,
)

def retry(times: int = 3, delay: float = 1.0):
    def deco(fn: Callable):
        @wraps(fn)
        def _inner(*args, **kwargs):
            last = None
            for _ in range(times):
                try:
                    return fn(*args, **kwargs)
                except RETRY_EXC as e:
                    last = e
                    time.sleep(delay)
            raise last
        return _inner
    return deco
