from abc import ABC, abstractmethod

from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax


class RichStringAbsStx(AbstractSyntax, ABC):
    @property
    @abstractmethod
    def spans_whole_line(self) -> bool:
        """If this syntax spans the whole (last) line."""
        raise NotImplementedError('abstract method')
