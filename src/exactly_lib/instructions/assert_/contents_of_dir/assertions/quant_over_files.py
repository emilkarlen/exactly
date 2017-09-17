import pathlib

from exactly_lib.instructions.assert_.contents_of_dir.assertions import common
from exactly_lib.instructions.assert_.contents_of_dir.assertions.common import DirContentsAssertionPart
from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.assert_.utils.file_contents import actual_files
from exactly_lib.instructions.assert_.utils.file_contents.parts import file_assertion_part
from exactly_lib.instructions.assert_.utils.file_contents.parts.contents_checkers import ResolvedComparisonActualFile
from exactly_lib.instructions.assert_.utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.named_element.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.named_element.symbol.value_resolvers.file_ref_with_symbol import StackedFileRef
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.logic import file_matcher as file_matcher_type
from exactly_lib.util.logic_types import Quantifier, ExpectationType


class QuantifiedAssertion(DirContentsAssertionPart):
    def __init__(self,
                 settings: common.Settings,
                 quantifier: Quantifier,
                 assertion_on_file_to_check: AssertionPart):
        super().__init__(settings, assertion_on_file_to_check.validator)
        self._quantifier = quantifier
        self._assertion_on_file_to_check = assertion_on_file_to_check

    @property
    def references(self) -> list:
        return self._settings.file_matcher.references + self._assertion_on_file_to_check.references

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              settings: common.Settings) -> common.Settings:
        checker = _Checker(self._settings,
                           self._quantifier,
                           self._assertion_on_file_to_check,
                           environment,
                           os_services)
        err_msg = checker.check()
        if err_msg:
            raise PfhFailException(err_msg)
        return settings


class _Checker:
    """
    Helper that keeps some environment related info as member variables,
    to avoid having to pass them around explicitly.
    """

    def __init__(self,
                 settings: common.Settings,
                 quantifier: Quantifier,
                 assertion_on_file_to_check: AssertionPart,
                 environment: InstructionEnvironmentForPostSdsStep,
                 os_services: OsServices
                 ):
        """
        :param assertion_on_file_to_check: An :class:`AssertionPart` that operates on a `ResolvedComparisonActualFile`
        """
        self.settings = settings
        self.quantifier = quantifier
        self._assertion_on_file_to_check = assertion_on_file_to_check
        self.environment = environment
        self.os_services = os_services
        self._destination_file_path_getter = file_assertion_part.DestinationFilePathGetter()
        self._dir_to_check = settings.path_to_check.resolve(environment.symbols)

    def check(self) -> str:
        if self.quantifier is Quantifier.ALL:
            if self.settings.expectation_type is ExpectationType.POSITIVE:
                return self.check__all__positive()
            else:
                return self.check__all__negative()
        else:
            if self.settings.expectation_type is ExpectationType.POSITIVE:
                return self.check__exists__positive()
            else:
                return self.check__exists__negative()

    def check__all__positive(self) -> str:
        for actual_file in self.resolved_actual_file_iter():
            self.check_file(actual_file)
        return None

    def check__all__negative(self) -> str:
        for actual_file in self.resolved_actual_file_iter():
            try:
                self.check_file(actual_file)
            except PfhFailException:
                return None
        raise PfhFailException('All files satisfies the contents assertion (TODO improve err msg)')

    def check__exists__positive(self) -> str:
        for actual_file in self.resolved_actual_file_iter():
            try:
                self.check_file(actual_file)
                return None
            except PfhFailException:
                pass
        raise PfhFailException('No file satisfies the contents assertion (TODO improve err msg)')

    def check__exists__negative(self) -> str:
        for actual_file in self.resolved_actual_file_iter():
            try:
                self.check_file(actual_file)
                return 'A file does satisfy the contents assertion (TODO improve err msg)'
            except PfhFailException:
                pass
        return None

    def resolved_actual_file_iter(self) -> iter:
        path_resolving_env = self.environment.path_resolving_environment_pre_or_post_sds
        path_to_check = self.settings.path_to_check.resolve_value_of_any_dependency(path_resolving_env)
        assert isinstance(path_to_check, pathlib.Path), 'Resolved value should be a path'
        file_matcher = self.settings.file_matcher.resolve(self.environment.symbols)
        selected_files = file_matcher_type.matching_files_in_dir(file_matcher, path_to_check)
        return map(self.new_resolved_actual_file, selected_files)

    def check_file(self, actual_file: ResolvedComparisonActualFile):
        self._assertion_on_file_to_check.check(self.environment,
                                               self.os_services,
                                               actual_file)

    def new_resolved_actual_file(self, path: pathlib.Path) -> ResolvedComparisonActualFile:
        return ResolvedComparisonActualFile(
            path,
            _FilePropertyDescriptorConstructorForFileInDir(self._dir_to_check,
                                                           path))


class _FilePropertyDescriptorConstructorForFileInDir(actual_files.FilePropertyDescriptorConstructor):
    def __init__(self,
                 dir_to_check: FileRef,
                 file_in_dir: pathlib.Path):
        self._dir_to_check = dir_to_check
        self._path = file_in_dir

    def construct_for_contents_attribute(self, contents_attribute: str) -> actual_files.PropertyDescriptor:
        path_resolver = FileRefConstant(
            StackedFileRef(self._dir_to_check, PathPartAsFixedPath(self._path.name))
        )
        return actual_files.path_value_description(
            actual_files.file_property_name(contents_attribute,
                                            actual_files.PLAIN_FILE_OBJECT_NAME),
            path_resolver)
