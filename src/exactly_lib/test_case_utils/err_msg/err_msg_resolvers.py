from abc import ABC
from typing import Sequence, Callable

from exactly_lib.type_system.error_message import ErrorMessageResolver, ErrorMessageResolvingEnvironment


class ErrorMessageResolverFromManyResolvers(ABC):
    def __init__(self,
                 parts: Sequence[ErrorMessageResolver],
                 separator: str = '\n',
                 first_line_prefix: str = ''):
        self._parts = parts
        self._separator = separator
        self._first_line_prefix = first_line_prefix

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        parts_output = [
            self._first_line_prefix + part.resolve(environment)
            for part in self._parts
        ]
        return self._separator.join(parts_output)


class ErrorMessageResolverFromFunction(ErrorMessageResolver):
    def __init__(self, resolver: Callable[[ErrorMessageResolvingEnvironment], str]):
        self._resolver = resolver

    def resolve(self, environment: ErrorMessageResolvingEnvironment) -> str:
        return self._resolver(environment)
