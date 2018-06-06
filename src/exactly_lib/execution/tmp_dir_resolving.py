import tempfile
from typing import Callable

SandboxRootDirNameResolver = Callable[[], str]


def mk_tmp_dir_with_prefix(dir_name_prefix: str) -> SandboxRootDirNameResolver:
    def ret_val() -> str:
        return tempfile.mkdtemp(prefix=dir_name_prefix)

    return ret_val
