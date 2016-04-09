import shlex


def file_name(fn: str) -> str:
    return shlex.quote(fn)
