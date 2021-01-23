from abc import ABC

from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax


class StringAbsStx(AbstractSyntax, ABC):
    pass


class NonHereDocStringAbsStx(StringAbsStx, ABC):
    pass
