from abc import ABC, abstractmethod
from typing import Tuple, Set, Optional

from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator, \
    constant_success_validator
from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.type_system.description import trace_renderers
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import WithTreeStructureDescription
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace, MatchingResult

LineMatcherLine = Tuple[int, str]

FIRST_LINE_NUMBER = 1


class LineMatcher(WithCachedTreeStructureDescriptionBase,
                  MatcherWTrace[LineMatcherLine],
                  ABC):
    """
    Matches text lines.

    A line is a tuple (line number, line contents).

    Line numbers start at 1.
    """

    @property
    def name(self) -> str:
        return self.option_description

    def _new_tb(self) -> TraceBuilder:
        return TraceBuilder(self.name)

    def matches_w_trace(self, line: LineMatcherLine) -> MatchingResult:
        mb_fail = self.matches_emr(line)

        tb = self._new_tb()

        if mb_fail is None:
            return tb.build_result(True)
        else:
            tb.details.append(
                trace_renderers.DetailsRendererOfErrorMessageResolver(mb_fail))
            return tb.build_result(False)

    def matches_emr(self, line: LineMatcherLine) -> Optional[ErrorMessageResolver]:
        if self.matches(line):
            return None
        else:
            return err_msg_resolvers.constant('Lines does not match')

    def matches(self, line: LineMatcherLine) -> bool:
        """
        :return: If the line matches the condition represented by the matcher
        """
        raise NotImplementedError('abstract method of ' + str(type(self)))


class LineMatcherValue(MultiDirDependentValue[LineMatcher], WithTreeStructureDescription, ABC):
    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set()

    def validator(self) -> PreOrPostSdsValueValidator:
        return constant_success_validator()

    @abstractmethod
    def value_when_no_dir_dependencies(self) -> LineMatcher:
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        pass

    @abstractmethod
    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> LineMatcher:
        """Gives the value, regardless of actual dependency."""
        pass
