import pathlib
from typing import Sequence, Optional, Iterator

from exactly_lib.definitions import actual_file_attributes
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.instructions.assert_.contents_of_dir import config, files_matchers
from exactly_lib.instructions.assert_.contents_of_dir.files_matchers import FilesMatcherResolverBase
from exactly_lib.symbol.data import file_ref_resolvers
from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.file_ref_resolver_impls.file_ref_with_symbol import StackedFileRef
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.err_msg import diff_msg_utils, diff_msg
from exactly_lib.test_case_utils.err_msg import path_description
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.file_system_element_matcher import \
    FileSystemElementReference, FileSystemElementPropertiesMatcher
from exactly_lib.test_case_utils.files_matcher.structure import FilesSource, FilesMatcherResolver, \
    HardErrorException, Environment
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment, PropertyDescriptor, \
    FilePropertyDescriptorConstructor, ErrorMessageResolver, ErrorMessageResolverFromFunction
from exactly_lib.type_system.logic import file_matcher as file_matcher_type
from exactly_lib.type_system.logic.string_matcher import DestinationFilePathGetter, FileToCheck
from exactly_lib.type_system.logic.string_transformer import IdentityStringTransformer
from exactly_lib.util.logic_types import Quantifier, ExpectationType


def quantified_matcher(settings: files_matchers.Settings,
                       quantifier: Quantifier,
                       matcher_on_existing_regular_file: StringMatcherResolver,
                       ) -> FilesMatcherResolver:
    return _QuantifiedMatcher(settings,
                              quantifier,
                              matcher_on_existing_regular_file)


class _QuantifiedMatcher(FilesMatcherResolverBase):
    def __init__(self,
                 settings: files_matchers.Settings,
                 quantifier: Quantifier,
                 matcher_on_existing_regular_file: StringMatcherResolver):
        super().__init__(settings, matcher_on_existing_regular_file.validator)
        self._quantifier = quantifier
        self._matcher_on_existing_regular_file = matcher_on_existing_regular_file

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._settings.file_matcher.references + self._matcher_on_existing_regular_file.references

    def matches(self,
                environment: Environment,
                files_source: FilesSource) -> Optional[ErrorMessageResolver]:
        checker = _Checker(self._settings,
                           self._quantifier,
                           self._matcher_on_existing_regular_file,
                           environment,
                           files_source)
        return checker.check()


class _Checker:
    """
    Helper that keeps some environment related info as member variables,
    to avoid having to pass them around explicitly.
    """

    def __init__(self,
                 settings: files_matchers.Settings,
                 quantifier: Quantifier,
                 matcher_on_existing_regular_file: StringMatcherResolver,
                 environment: Environment,
                 files_source: FilesSource,
                 ):
        self.settings = settings
        self.quantifier = quantifier
        pre = environment.path_resolving_environment
        self.path_resolving_environment = pre

        self.matcher_on_existing_regular_file = (matcher_on_existing_regular_file
                                                 .resolve(pre.symbols)
                                                 .value_of_any_dependency(pre.home_and_sds))
        self.environment = environment
        self.files_source = files_source
        self._dir_to_check = files_source.path_of_dir.resolve(pre.symbols)
        self.error_reporting = _ErrorReportingHelper(settings,
                                                     files_source.path_of_dir,
                                                     quantifier)
        self.is_existing_regular_file_checker = FileSystemElementPropertiesMatcher(
            file_properties.ActualFilePropertiesResolver(file_properties.FileType.REGULAR,
                                                         follow_symlinks=True)
        )
        self.models_factory = _ModelsFactory(environment, files_source)

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
            mb_failure = self.check_file(actual_file)
            if mb_failure is not None:
                return mb_failure
        return None

    def check__all__negative(self) -> Optional[ErrorMessageResolver]:
        for actual_file in self.resolved_actual_file_iter():
            mb_failure = self.check_file(actual_file)
            if mb_failure is not None:
                return None
        return self.error_reporting.err_msg_for_dir__all_satisfies()

    def check__exists__positive(self) -> Optional[ErrorMessageResolver]:
        for actual_file in self.resolved_actual_file_iter():
            mb_failure = self.check_file(actual_file)
            if mb_failure is None:
                return None
        return self.error_reporting.err_msg_for_dir('no file satisfy')

    def check__exists__negative(self) -> Optional[ErrorMessageResolver]:
        for actual_file in self.resolved_actual_file_iter():
            mb_failure = self.check_file(actual_file)
            if mb_failure is None:
                return self.error_reporting.err_msg_for_file_in_dir('one file satisfies', actual_file)
        return None

    def resolved_actual_file_iter(self) -> Iterator[pathlib.Path]:
        pre = self.path_resolving_environment
        path_to_check = self.files_source.path_of_dir.resolve_value_of_any_dependency(pre)
        assert isinstance(path_to_check, pathlib.Path), 'Resolved value should be a path'
        file_matcher = self.settings.file_matcher.resolve(pre.symbols)
        return file_matcher_type.matching_files_in_dir(file_matcher, path_to_check)

    def check_file(self, path: pathlib.Path) -> Optional[ErrorMessageResolver]:
        mb_error = self.is_existing_regular_file_checker.matches(
            self.models_factory.file_system_element_reference(path))
        if mb_error is not None:
            raise HardErrorException(mb_error)

        return self.matcher_on_existing_regular_file.matches(self.models_factory.file_to_check(path))


class _ModelsFactory:
    def __init__(self,
                 environment: Environment,
                 files_source: FilesSource,
                 ):
        self._id_trans = IdentityStringTransformer()
        self._tmp_file_space = environment.tmp_files_space
        self._dir_to_check_resolver = files_source.path_of_dir
        self._dir_to_check = files_source.path_of_dir.resolve(environment.path_resolving_environment.symbols)
        self._destination_file_path_getter = DestinationFilePathGetter()

    def file_to_check(self, path: pathlib.Path) -> FileToCheck:
        return FileToCheck(path,
                           _FilePropertyDescriptorConstructorForFileInDir(self._dir_to_check,
                                                                          path),
                           self._tmp_file_space,
                           self._id_trans,
                           self._destination_file_path_getter)

    def file_system_element_reference(self, path: pathlib.Path) -> FileSystemElementReference:
        return FileSystemElementReference(
            file_ref_resolvers.constant(_path_value_for_file_in_checked_dir(self._dir_to_check, path)),
            path
        )


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
                                actual_file: pathlib.Path) -> ErrorMessageResolver:
        def resolve(environment: ErrorMessageResolvingEnvironment) -> str:
            failing_file_description_lines = path_description.lines_for_path_value(
                _path_value_for_file_in_checked_dir(self._dir_to_check.resolve(environment.symbols),
                                                    actual_file),
                environment.tcds,
            )
            actual_info = diff_msg.ActualInfo(single_line_value, failing_file_description_lines)
            return self._diff_failure_info_for_dir().resolve(environment,
                                                             actual_info).error_message()

        return ErrorMessageResolverFromFunction(resolve)

    def _diff_failure_info_for_dir(self) -> diff_msg_utils.DiffFailureInfoResolver:
        property_descriptor = path_description.path_value_description(
            property_description.file_property_name(
                actual_file_attributes.CONTENTS_ATTRIBUTE,
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
            property_description.file_property_name(contents_attribute,
                                                    actual_file_attributes.PLAIN_FILE_OBJECT_NAME),
            path_resolver)


def _path_value_for_file_in_checked_dir(dir_to_check: FileRef, file_in_dir: pathlib.Path) -> FileRef:
    return StackedFileRef(dir_to_check, file_refs.constant_path_part(file_in_dir.name))
