import pathlib
from typing import Sequence, Callable

from exactly_lib.test_case_utils.err_msg import path_description
from exactly_lib.type_system.error_message import ErrorMessageResolver, ErrorMessageResolvingEnvironment, \
    ConstantErrorMessageResolver


def itemized_list(items: Sequence[ErrorMessageResolver],
                  item_header_prefix: str = '* ',
                  separator: str = '\n') -> ErrorMessageResolver:
    return ErrorMessageResolverList(items, item_header_prefix, separator)


def section(header: str,
            contents: ErrorMessageResolver,
            separator: str = '\n\n') -> ErrorMessageResolver:
    return ErrorMessageResolverSection(header, contents, separator)


def sequence_of_parts(parts: Sequence[ErrorMessageResolver],
                      separator: str = '\n\n') -> ErrorMessageResolver:
    return ErrorMessageResolverParts(parts, separator)


def of_function(resolver: Callable[[ErrorMessageResolvingEnvironment], str]) -> ErrorMessageResolver:
    return ErrorMessageResolverFromFunction(resolver)


def constant(msg: str) -> ErrorMessageResolver:
    return ConstantErrorMessageResolver(msg)


def of_path(path: pathlib.Path) -> ErrorMessageResolver:
    return ErrorMessageResolverOfPath(path)


class ErrorMessageResolverOfPath(ErrorMessageResolver):
    def __init__(self, path: pathlib.Path):
        self._path = path

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        return path_description.path_value_with_relativity_name_prefix_str(self._path, environment.tcds)


class ErrorMessageResolverList(ErrorMessageResolver):
    """Simple list"""

    def __init__(self,
                 items: Sequence[ErrorMessageResolver],
                 item_header_prefix: str = '* ',
                 separator: str = '\n'):
        self._items = items
        self._separator = separator
        self._item_header_prefix = item_header_prefix

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        parts_output = [
            self._item_header_prefix + part.resolve(environment)
            for part in self._items
        ]
        return self._separator.join(parts_output)


class ErrorMessageResolverParts(ErrorMessageResolver):
    """A sequence of resolvers separated by a constant string"""

    def __init__(self,
                 parts: Sequence[ErrorMessageResolver],
                 separator: str = '\n\n'):
        self._parts = parts
        self._separator = separator

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        parts_output = [
            part.resolve(environment)
            for part in self._parts
        ]
        return self._separator.join(parts_output)


class ErrorMessageResolverSection(ErrorMessageResolver):
    """Simple section with a header and contents"""

    def __init__(self,
                 header: str,
                 contents: ErrorMessageResolver,
                 separator: str = '\n\n'):
        self._header = header
        self._contents = contents
        self._separator = separator

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        return self._separator.join([self._header,
                                     self._contents.resolve(environment)])


class ErrorMessageResolverFromFunction(ErrorMessageResolver):
    def __init__(self, resolver: Callable[[ErrorMessageResolvingEnvironment], str]):
        self._resolver = resolver

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        return self._resolver(environment)
