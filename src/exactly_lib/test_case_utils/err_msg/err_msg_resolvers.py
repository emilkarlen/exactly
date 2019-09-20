from typing import Sequence, Callable

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case_utils.err_msg2 import path_rendering
from exactly_lib.type_system.data.path_describer import PathDescriberForPrimitive
from exactly_lib.type_system.err_msg import error_message
from exactly_lib.type_system.err_msg.error_message import ErrorMessageResolver, ConstantErrorMessageResolver


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


def of_function(resolver: Callable[[], str]) -> ErrorMessageResolver:
    return ErrorMessageResolverFromFunction(resolver)


def constant(msg: str) -> ErrorMessageResolver:
    return ConstantErrorMessageResolver(msg)


def text_doc(message: TextRenderer) -> ErrorMessageResolver:
    return error_message.OfTextDoc(message)


def of_path(path: PathDescriberForPrimitive) -> ErrorMessageResolver:
    return ErrorMessageResolverOfPath(path)


class ErrorMessageResolverList(ErrorMessageResolver):
    """Simple list"""

    def __init__(self,
                 items: Sequence[ErrorMessageResolver],
                 item_header_prefix: str = '* ',
                 separator: str = '\n'):
        self._items = items
        self._separator = separator
        self._item_header_prefix = item_header_prefix

    def resolve(self) -> str:
        parts_output = [
            self._item_header_prefix + part.resolve()
            for part in self._items
        ]
        return self._separator.join(parts_output)


class ErrorMessageResolverOfPath(ErrorMessageResolver):
    def __init__(self, path: PathDescriberForPrimitive):
        self._path = path

    def resolve(self) -> str:
        return '\n'.join(path_rendering.path_strings(self._path))


class ErrorMessageResolverParts(ErrorMessageResolver):
    """A sequence of resolvers separated by a constant string"""

    def __init__(self,
                 parts: Sequence[ErrorMessageResolver],
                 separator: str = '\n\n'):
        self._parts = parts
        self._separator = separator

    def resolve(self) -> str:
        parts_output = [
            part.resolve()
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

    def resolve(self) -> str:
        return self._separator.join([self._header,
                                     self._contents.resolve()])


class ErrorMessageResolverFromFunction(ErrorMessageResolver):
    def __init__(self, resolver: Callable[[], str]):
        self._resolver = resolver

    def resolve(self) -> str:
        return self._resolver()
