from typing import Optional

from exactly_lib.execution.predefined_properties import os_environ_getter
from exactly_lib.util import functional

ENV_VARS__DEFAULT = None
ENV_VARS_GETTER__DEFAULT = os_environ_getter
TIMEOUT__DEFAULT = None

TIMEOUT__NONE_TOKEN = 'none'


def render_timeout_value(x: Optional[int]) -> str:
    return functional.reduce_optional(str, TIMEOUT__NONE_TOKEN, x)
