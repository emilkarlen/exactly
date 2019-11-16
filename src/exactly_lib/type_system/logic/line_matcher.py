from abc import ABC, abstractmethod
from typing import Tuple

from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator, \
    constant_success_validator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatcherDdv

LineMatcherLine = Tuple[int, str]

FIRST_LINE_NUMBER = 1


class LineMatcher(MatcherWTraceAndNegation[LineMatcherLine], ABC):
    """
    Matches text lines.

    A line is a tuple (line number, line contents).

    Line numbers start at 1.
    """
    pass


class LineMatcherDdv(MatcherDdv[LineMatcherLine], ABC):
    @property
    def validator(self) -> PreOrPostSdsValueValidator:
        return constant_success_validator()

    @abstractmethod
    def value_of_any_dependency(self, tcds: Tcds) -> LineMatcher:
        """Gives the value, regardless of actual dependency."""
        pass
