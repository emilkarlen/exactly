import os

from exactly_lib.test_case import executable_factories
from exactly_lib.test_case.os_services import OsServices


class OsServicesError(Exception):
    def __init__(self, msg: str):
        self.msg = msg


def new_for_current_os() -> OsServices:
    """
    :raises :class:`OsServicesError`: The current operating system is not supported
    """
    return new_for_os(os.name)


def new_for_current_os__with_environ() -> OsServices:
    """
    :raises :class:`OsServicesError`: The current operating system is not supported
    """
    return new_for_current_os()


def new_for_os(os_name: str) -> OsServices:
    """
    :raises :class:`OsServicesError`: The given operating system is not supported
    """
    from exactly_lib.test_case_utils.os_services import impl
    try:
        executable_factory = executable_factories.get_factory_for_operating_system(os_name)
    except KeyError:
        raise OsServicesError(
            'Unsupported Operating System: {}'.format(os_name)
        )
    return impl.OsServicesForAnyOs(executable_factory)
