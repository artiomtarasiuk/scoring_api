import functools
import logging
import time
from typing import Any, Optional

import redis


def retry(use_cache: bool = False):
    def retry_decorator(method):
        @functools.wraps(method)
        def retry_method(self, *args, **kwargs):
            if use_cache:
                try:
                    return method(self, *args, **kwargs)
                except Exception as e:
                    logging.info(f"Cache is unavailable: {e}")
                    return None
            cnt = 1
            retries = self.RETRY_NUMBER
            while cnt <= retries:
                try:
                    return method(self, *args, **kwargs)
                except redis.exceptions.ConnectionError as e:
                    base_msg = f"Redis server is not available: {e}."
                    if cnt > 1:
                        base_msg += f"\n Attempt {cnt} out of {retries}"
                    logging.info(base_msg)
                    cnt += 1
                    time.sleep(1)
            raise redis.exceptions.ConnectionError

        return retry_method

    return retry_decorator


class Storage:
    RETRY_NUMBER = 5

    def __init__(self):
        self.client = redis.Redis()

    def health_check(self) -> bool:
        return self.client.ping()

    @retry(use_cache=True)
    def cache_set(self, key: str, value: Any, seconds: int) -> bool:
        return self.client.set(key, value, ex=seconds)

    @retry(use_cache=False)
    def get(self, key: str) -> Any:
        return self.client.get(key)

    @retry(use_cache=True)
    def cache_get(self, key: str) -> Optional[Any]:
        return self.client.get(key)
