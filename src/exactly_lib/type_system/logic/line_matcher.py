from abc import ABC, abstractmethod
from typing import Tuple, Set, Optional

from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator, constant_success_validator
from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.error_message import ErrorMessageResolver, ConstantErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import Matcher

LineMatcherLine = Tuple[int, str]

FIRST_LINE_NUMBER = 1


class LineMatcher(Matcher[LineMatcherLine]):
    """
    Matches text lines.

    A line is a tuple (line number, line contents).

    Line numbers start at 1.
    """

    def matches2(self, line: LineMatcherLine) -> Optional[ErrorMessageResolver]:
        if self.matches(line):
            return None
        else:
            return ConstantErrorMessageResolver('Lines does not match')

    def matches(self, line: LineMatcherLine) -> bool:
        """
        :return: If the line matches the condition represented by the matcher
        """
        raise NotImplementedError('abstract method')


class LineMatcherValue(MultiDirDependentValue[LineMatcher], ABC):
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
