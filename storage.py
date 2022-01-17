import functools
import logging
import time
from typing import Any, Optional

import redis


def retry(retry_number: int = None):
    def retry_decorator(method):
        @functools.wraps(method)
        def retry_method(self, *args, **kwargs):
            cnt = 1
            retries = retry_number or self.RETRY_NUMBER
            while cnt <= retries:
                try:
                    return method(self, *args, **kwargs)
                except redis.exceptions.ConnectionError as e:
                    base_msg = f"Redis server is not available: {e}"
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

    @retry
    def cache_set(self, key: str, value: Any, seconds: int) -> bool:
        return self.client.set(key, value, ex=seconds)

    @retry
    def get(self, key: str) -> Any:
        return self.client.get(key)

    @retry(retry_number=1)
    def cache_get(self, key: str) -> Optional[Any]:
        return self.client.get(key)
