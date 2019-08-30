from typing import Sequence, Callable

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case_utils.err_msg2 import path_rendering
from exactly_lib.test_case_utils.err_msg2.path_describer import PathDescriberForPrimitive
from exactly_lib.type_system import error_message
from exactly_lib.type_system.error_message import ErrorMessageResolver, ErrorMessageResolvingEnvironment, \
    ConstantErrorMessageResolver, ErrorMessageResolverOfFixed, ErrorMessageFixedResolver


def resolver_of_fixed(fixed: ErrorMessageFixedResolver) -> ErrorMessageResolver:
    return ErrorMessageResolverOfFixed(fixed)


def itemized_list(items: Sequence[ErrorMessageResolver],
                  item_header_prefix: str = '* ',
                  separator: str = '\n') -> ErrorMessageResolver:
    return ErrorMessageResolverList(items, item_header_prefix, separator)


def itemized_list__fixed(items: Sequence[ErrorMessageFixedResolver],
                         item_header_prefix: str = '* ',
                         separator: str = '\n') -> ErrorMessageFixedResolver:
    return ErrorMessageFixedResolverList(items, item_header_prefix, separator)


def section(header: str,
            contents: ErrorMessageResolver,
            separator: str = '\n\n') -> ErrorMessageResolver:
    return ErrorMessageResolverSection(header, contents, separator)


def section__fixed(header: str,
                   contents: ErrorMessageFixedResolver,
                   separator: str = '\n\n') -> ErrorMessageFixedResolver:
    return ErrorMessageFixedResolverSection(header, contents, separator)


def sequence_of_parts(parts: Sequence[ErrorMessageResolver],
                      separator: str = '\n\n') -> ErrorMessageResolver:
    return ErrorMessageResolverParts(parts, separator)


def sequence_of_parts__fixed(parts: Sequence[ErrorMessageFixedResolver],
                             separator: str = '\n\n') -> ErrorMessageFixedResolver:
    return ErrorMessageFixedResolverParts(parts, separator)


def of_function(resolver: Callable[[ErrorMessageResolvingEnvironment], str]) -> ErrorMessageResolver:
    return ErrorMessageResolverFromFunction(resolver)


def constant(msg: str) -> ErrorMessageResolver:
    return ErrorMessageResolverOfFixed(ConstantErrorMessageResolver(msg))


def constant__fixed(msg: str) -> ErrorMessageFixedResolver:
    return ConstantErrorMessageResolver(msg)


def text_doc(message: TextRenderer) -> ErrorMessageResolver:
    return ErrorMessageResolverOfFixed(error_message.OfTextDoc(message))


def text_doc_fixed(message: TextRenderer) -> ErrorMessageFixedResolver:
    return error_message.OfTextDoc(message)


def of_path(path: PathDescriberForPrimitive) -> ErrorMessageResolver:
    return ErrorMessageResolverOfFixed(ErrorMessageResolverOfPath(path))


def of_path__fixed(path: PathDescriberForPrimitive) -> ErrorMessageFixedResolver:
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

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        parts_output = [
            self._item_header_prefix + part.resolve(environment)
            for part in self._items
        ]
        return self._separator.join(parts_output)


class ErrorMessageFixedResolverList(ErrorMessageFixedResolver):
    """Simple list"""

    def __init__(self,
                 items: Sequence[ErrorMessageFixedResolver],
                 item_header_prefix: str = '* ',
                 separator: str = '\n'):
        self._items = items
        self._separator = separator
        self._item_header_prefix = item_header_prefix

    def message(self) -> str:
        parts_output = [
            self._item_header_prefix + part.message()
            for part in self._items
        ]
        return self._separator.join(parts_output)


class ErrorMessageResolverOfPath(ErrorMessageFixedResolver):
    def __init__(self, path: PathDescriberForPrimitive):
        self._path = path

    def message(self) -> str:
        return '\n'.join(path_rendering.path_strings(self._path))


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


class ErrorMessageFixedResolverParts(ErrorMessageFixedResolver):
    """A sequence of resolvers separated by a constant string"""

    def __init__(self,
                 parts: Sequence[ErrorMessageFixedResolver],
                 separator: str = '\n\n'):
        self._parts = parts
        self._separator = separator

    def message(self) -> str:
        parts_output = [
            part.message()
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


class ErrorMessageFixedResolverSection(ErrorMessageFixedResolver):
    """Simple section with a header and contents"""

    def __init__(self,
                 header: str,
                 contents: ErrorMessageFixedResolver,
                 separator: str = '\n\n'):
        self._header = header
        self._contents = contents
        self._separator = separator

    def message(self) -> str:
        return self._separator.join([self._header,
                                     self._contents.message()])


class ErrorMessageResolverFromFunction(ErrorMessageResolver):
    def __init__(self, resolver: Callable[[ErrorMessageResolvingEnvironment], str]):
        self._resolver = resolver

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        return self._resolver(environment)
