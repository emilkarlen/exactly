from abc import ABC
from typing import Optional

from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedNameAndTreeStructureDescriptionBase
from exactly_lib.test_case_utils.string_matcher.negation import StringMatcherNegation
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck


class StringMatcherImplBase(WithCachedNameAndTreeStructureDescriptionBase,
                            MatcherWTraceAndNegation[FileToCheck],
                            ABC):

    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        """
        :raises HardErrorException: In case of HARD ERROR
        :return: None iff match
        """
        raise NotImplementedError('deprecated')

    @property
    def negation(self) -> StringMatcher:
        return StringMatcherNegation(self)

    def _new_tb(self) -> TraceBuilder:
        return TraceBuilder(self.name)
