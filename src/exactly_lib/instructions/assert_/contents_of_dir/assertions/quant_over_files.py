import pathlib
from typing import Sequence, Any, Optional

from exactly_lib.definitions import actual_file_attributes
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.instructions.assert_.contents_of_dir import config, files_matchers
from exactly_lib.instructions.assert_.contents_of_dir.files_matcher import FilesSource, FilesMatcherResolver
from exactly_lib.instructions.assert_.contents_of_dir.files_matchers import FilesMatcherResolverBase
from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart
from exactly_lib.instructions.assert_.utils.file_contents import actual_files
from exactly_lib.instructions.assert_.utils.file_contents.parts.contents_checkers import ComparisonActualFile
from exactly_lib.symbol.data import file_ref_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.file_ref_resolver_impls.file_ref_with_symbol import StackedFileRef
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.err_msg import diff_msg_utils, diff_msg
from exactly_lib.test_case_utils.err_msg import path_description
from exactly_lib.test_case_utils.return_pfh_via_exceptions import PfhFailException
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment, PropertyDescriptor, \
    FilePropertyDescriptorConstructor, ErrorMessageResolver, ErrorMessageResolverFromFunction
from exactly_lib.type_system.logic import file_matcher as file_matcher_type
from exactly_lib.type_system.logic.string_matcher import DestinationFilePathGetter
from exactly_lib.util.logic_types import Quantifier, ExpectationType


def quantified_matcher(settings: files_matchers.Settings,
                       quantifier: Quantifier,
                       assertion_on_file_to_check: AssertionPart[ComparisonActualFile, Any]
                       ) -> FilesMatcherResolver:
    return _QuantifiedMatcher(settings,
                              quantifier,
                              assertion_on_file_to_check)


class _QuantifiedMatcher(FilesMatcherResolverBase):
    def __init__(self,
                 settings: files_matchers.Settings,
                 quantifier: Quantifier,
                 assertion_on_file_to_check: AssertionPart[ComparisonActualFile, Any]):
        super().__init__(settings, assertion_on_file_to_check.validator)
        self._quantifier = quantifier
        self._assertion_on_file_to_check = assertion_on_file_to_check

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._settings.file_matcher.references + self._assertion_on_file_to_check.references

    def matches(self,
                environment: InstructionEnvironmentForPostSdsStep,
                os_services: OsServices,
                files_source: FilesSource) -> Optional[ErrorMessageResolver]:
        checker = _Checker(self._settings,
                           self._quantifier,
                           self._assertion_on_file_to_check,
                           environment,
                           files_source,
                           os_services)
        return checker.check()


class _Checker:
    """
    Helper that keeps some environment related info as member variables,
    to avoid having to pass them around explicitly.
    """

    def __init__(self,
                 settings: files_matchers.Settings,
                 quantifier: Quantifier,
                 assertion_on_file_to_check: AssertionPart[ComparisonActualFile, Any],
                 environment: InstructionEnvironmentForPostSdsStep,
                 files_source: FilesSource,
                 os_services: OsServices
                 ):
        self.settings = settings
        self.quantifier = quantifier
        self._assertion_on_file_to_check = assertion_on_file_to_check
        self.environment = environment
        self.files_source = files_source
        self.os_services = os_services
        self._destination_file_path_getter = DestinationFilePathGetter()
        self._dir_to_check = files_source.path_of_dir.resolve(environment.symbols)
        self.error_reporting = _ErrorReportingHelper(settings,
                                                     files_source.path_of_dir,
                                                     quantifier)

    def check(self) -> Optional[ErrorMessageResolver]:
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

    def check__all__positive(self) -> Optional[ErrorMessageResolver]:
        for actual_file in self.resolved_actual_file_iter():
            self.check_file(actual_file)
        return None

    def check__all__negative(self) -> Optional[ErrorMessageResolver]:
        for actual_file in self.resolved_actual_file_iter():
            try:
                self.check_file(actual_file)
            except PfhFailException:
                return None
        return self.error_reporting.err_msg_for_dir__all_satisfies()

    def check__exists__positive(self) -> Optional[ErrorMessageResolver]:
        for actual_file in self.resolved_actual_file_iter():
            try:
                self.check_file(actual_file)
                return None
            except PfhFailException:
                pass
        return self.error_reporting.err_msg_for_dir('no file satisfy')

    def check__exists__negative(self) -> Optional[ErrorMessageResolver]:
        for actual_file in self.resolved_actual_file_iter():
            try:
                self.check_file(actual_file)
                return self.error_reporting.err_msg_for_file_in_dir('one file satisfies', actual_file)
            except PfhFailException:
                pass
        return None

    def resolved_actual_file_iter(self) -> iter:
        path_resolving_env = self.environment.path_resolving_environment_pre_or_post_sds
        path_to_check = self.files_source.path_of_dir.resolve_value_of_any_dependency(path_resolving_env)
        assert isinstance(path_to_check, pathlib.Path), 'Resolved value should be a path'
        file_matcher = self.settings.file_matcher.resolve(self.environment.symbols)
        selected_files = file_matcher_type.matching_files_in_dir(file_matcher, path_to_check)
        return map(self.new_resolved_actual_file, selected_files)

    def check_file(self, actual_file: ComparisonActualFile):
        self._assertion_on_file_to_check.check(self.environment,
                                               self.os_services,
                                               None,
                                               actual_file)

    def new_resolved_actual_file(self, path: pathlib.Path) -> ComparisonActualFile:
        return ComparisonActualFile(
            path,
            _path_value_for_file_in_checked_dir(self._dir_to_check, path),
            _FilePropertyDescriptorConstructorForFileInDir(self._dir_to_check,
                                                           path))


class _ErrorReportingHelper:
    def __init__(self,
                 settings: files_matchers.Settings,
                 dir_to_check: FileRefResolver,
                 quantifier: Quantifier,
                 ):
        self.settings = settings
        self.quantifier = quantifier
        self._destination_file_path_getter = DestinationFilePathGetter()
        self._dir_to_check = dir_to_check

    def err_msg_for_dir__all_satisfies(self) -> ErrorMessageResolver:
        single_line_value = instruction_arguments.QUANTIFIER_ARGUMENTS[self.quantifier] + ' file satisfies'
        return self.err_msg_for_dir(single_line_value)

    def err_msg_for_dir(self, single_line_value: str) -> ErrorMessageResolver:
        def resolve(environment: ErrorMessageResolvingEnvironment) -> str:
            return self._diff_failure_info_for_dir().resolve(environment,
                                                             diff_msg.ActualInfo(single_line_value)).error_message()

        return ErrorMessageResolverFromFunction(resolve)

    def err_msg_for_file_in_dir(self,
                                single_line_value: str,
                                actual_file: ComparisonActualFile) -> ErrorMessageResolver:
        def resolve(environment: ErrorMessageResolvingEnvironment) -> str:
            failing_file_description_lines = path_description.lines_for_path_value(
                _path_value_for_file_in_checked_dir(self._dir_to_check.resolve(environment.symbols),
                                                    actual_file.actual_file_path),
                environment.tcds,
            )
            actual_info = diff_msg.ActualInfo(single_line_value, failing_file_description_lines)
            return self._diff_failure_info_for_dir().resolve(environment,
                                                             actual_info).error_message()

        return ErrorMessageResolverFromFunction(resolve)

    def _diff_failure_info_for_dir(self) -> diff_msg_utils.DiffFailureInfoResolver:
        property_descriptor = path_description.path_value_description(
            actual_files.file_property_name(actual_file_attributes.CONTENTS_ATTRIBUTE,
                                            actual_file_attributes.PLAIN_DIR_OBJECT_NAME),
            self._dir_to_check)
        return diff_msg_utils.DiffFailureInfoResolver(
            property_descriptor,
            self.settings.expectation_type,
            diff_msg_utils.ConstantExpectedValueResolver(self._description_of_expected()),
        )

    def _description_of_expected(self):
        return ' '.join([instruction_arguments.QUANTIFIER_ARGUMENTS[self.quantifier],
                         config.QUANTIFICATION_OVER_FILE_ARGUMENT,
                         'satisfies',
                         syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.singular_name])


class _FilePropertyDescriptorConstructorForFileInDir(FilePropertyDescriptorConstructor):
    def __init__(self,
                 dir_to_check: FileRef,
                 file_in_dir: pathlib.Path):
        self._dir_to_check = dir_to_check
        self._path = file_in_dir

    def construct_for_contents_attribute(self,
                                         contents_attribute: str) -> PropertyDescriptor:
        path_resolver = file_ref_resolvers.constant(
            _path_value_for_file_in_checked_dir(self._dir_to_check, self._path)
        )
        return path_description.path_value_description(
            actual_files.file_property_name(contents_attribute,
                                            actual_file_attributes.PLAIN_FILE_OBJECT_NAME),
            path_resolver)


def _path_value_for_file_in_checked_dir(dir_to_check: FileRef, file_in_dir: pathlib.Path) -> FileRef:
    return StackedFileRef(dir_to_check, file_refs.constant_path_part(file_in_dir.name))
