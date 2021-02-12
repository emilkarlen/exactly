from typing import Dict

from exactly_lib.execution.configuration import PredefinedProperties


def get_empty_environ() -> Dict[str, str]:
    return dict()


def new_empty() -> PredefinedProperties:
    return PredefinedProperties(
        default_environ_getter=get_empty_environ,
        environ=None,
    )
