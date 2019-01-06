from abc import ABC, abstractmethod
from typing import Optional

from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.resolver_structure import LogicValueResolver
from exactly_lib.test_case.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_utils.files_matcher.new_model import FilesMatcherModel
from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.file_utils import TmpDirFileSpace


class HardErrorException(Exception):
    def __init__(self, error: ErrorMessageResolver):
        self._error = error

    @property
    def error(self) -> ErrorMessageResolver:
        return self._error


class Environment:
    def __init__(self,
                 path_resolving_environment: PathResolvingEnvironmentPreOrPostSds,
                 tmp_files_space: TmpDirFileSpace,
                 ):
        self.path_resolving_environment = path_resolving_environment
        self.tmp_files_space = tmp_files_space


class FilesMatcherResolver(LogicValueResolver, ABC):

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.FILES_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.FILES_MATCHER

    @abstractmethod
    def validator(self) -> PreOrPostSdsValidator:
        pass

    @abstractmethod
    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        """
        :raises HardErrorException: In case of HARD ERROR
        :return: None iff match
        """
        pass

    @property
    @abstractmethod
    def negation(self):
        """
        :rtype FilesMatcherResolver
        :return: A matcher that matches the negation of this matcher
        """
        pass
