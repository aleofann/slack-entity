import time
import requests
from functools import wraps


def exception_retry(retries=3, backoff=0.5):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attemp {i+1} of {retries}")

                    if i == retries - 1:
                        return e

                    sleep = backoff * (2 ** i)
                    time.sleep(sleep)
        return wrapper
    return decorator