import os
from typing import Dict


def os_environ_getter() -> Dict[str, str]:
    return dict(os.environ)
