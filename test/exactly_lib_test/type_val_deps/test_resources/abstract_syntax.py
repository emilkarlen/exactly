from abc import ABC

from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax


class TypeAbsStx(AbstractSyntax, ABC):
    """Base class for organising abstract syntax of types"""
    pass


class DataTypeAbsStx(TypeAbsStx, ABC):
    """Base class for organising abstract syntax of data types"""
    pass


class LogicTypeAbsStx(TypeAbsStx, ABC):
    """Base class for organising abstract syntax of logic types"""
    pass


class MatcherTypeAbsStx(LogicTypeAbsStx, ABC):
    """Base class for organising abstract syntax of matcher types"""
    pass
