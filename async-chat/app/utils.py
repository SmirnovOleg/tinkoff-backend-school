import time


def generate_client_id() -> str:
    return str(int(time.monotonic() * (10 ** 9)))
