from typing import Sequence, Callable

from exactly_lib.type_system.error_message import ErrorMessageResolver, ErrorMessageResolvingEnvironment


def itemized_list(items: Sequence[ErrorMessageResolver],
                  item_header_prefix: str = '* ',
                  separator: str = '\n') -> ErrorMessageResolver:
    return ErrorMessageResolverList(items, item_header_prefix, separator)


def section(header: str,
            contents: ErrorMessageResolver,
            separator: str = '\n\n') -> ErrorMessageResolver:
    return ErrorMessageResolverSection(header, contents, separator)


def of_function(resolver: Callable[[ErrorMessageResolvingEnvironment], str]) -> ErrorMessageResolver:
    return ErrorMessageResolverFromFunction(resolver)


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
