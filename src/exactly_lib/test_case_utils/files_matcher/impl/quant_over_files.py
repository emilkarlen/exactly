from typing import Sequence, Optional, Iterator

from exactly_lib.definitions import actual_file_attributes
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.symbol.data import file_ref_resolvers
from exactly_lib.symbol.files_matcher import FilesMatcherResolver, \
    Environment, FileModel, FilesMatcherModel, FilesMatcherValue
from exactly_lib.symbol.resolver_structure import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.err_msg import diff_msg_utils, diff_msg
from exactly_lib.test_case_utils.err_msg import path_description
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.file_system_element_matcher import \
    FileSystemElementReference, FileSystemElementPropertiesMatcher
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.test_case_utils.files_matcher.files_matchers import FilesMatcherResolverBase
from exactly_lib.type_system.error_message import ErrorMessageResolvingEnvironment, PropertyDescriptor, \
    FilePropertyDescriptorConstructor, ErrorMessageResolver, ErrorMessageResolverFromFunction
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.string_matcher import DestinationFilePathGetter, FileToCheck, StringMatcherValue
from exactly_lib.type_system.logic.string_transformer import IdentityStringTransformer
from exactly_lib.util import logic_types
from exactly_lib.util.logic_types import Quantifier, ExpectationType
from exactly_lib.util.symbol_table import SymbolTable


def quantified_matcher(expectation_type: ExpectationType,
                       quantifier: Quantifier,
                       matcher_on_existing_regular_file: StringMatcherResolver,
                       ) -> FilesMatcherResolver:
    return _QuantifiedMatcher(expectation_type,
                              quantifier,
                              matcher_on_existing_regular_file)


class _QuantifiedMatcherValue(FilesMatcherValue):
    def __init__(self,
                 expectation_type: ExpectationType,
                 quantifier: Quantifier,
                 matcher_on_existing_regular_file: StringMatcherValue):
        self._expectation_type = expectation_type
        self._quantifier = quantifier
        self._matcher_on_existing_regular_file = matcher_on_existing_regular_file

    @property
    def negation(self) -> FilesMatcherValue:
        return _QuantifiedMatcherValue(
            logic_types.negation(self._expectation_type),
            self._quantifier,
            self._matcher_on_existing_regular_file,
        )

    def matches(self,
                environment: Environment,
                files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        checker = _Checker(self._expectation_type,
                           self._quantifier,
                           self._matcher_on_existing_regular_file,
                           environment,
                           files_source)
        return checker.check()


class _QuantifiedMatcher(FilesMatcherResolverBase):
    def __init__(self,
                 expectation_type: ExpectationType,
                 quantifier: Quantifier,
                 matcher_on_existing_regular_file: StringMatcherResolver):
        super().__init__(expectation_type, matcher_on_existing_regular_file.validator)
        self._quantifier = quantifier
        self._matcher_on_existing_regular_file = matcher_on_existing_regular_file

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._matcher_on_existing_regular_file.references

    def resolve(self, symbols: SymbolTable) -> FilesMatcherValue:
        return _QuantifiedMatcherValue(
            self._expectation_type,
            self._quantifier,
            self._matcher_on_existing_regular_file.resolve(symbols),
        )

    @property
    def negation(self) -> FilesMatcherResolver:
        return _QuantifiedMatcher(
            logic_types.negation(self._expectation_type),
            self._quantifier,
            self._matcher_on_existing_regular_file
        )


class _Checker:
    """
    Helper that keeps some environment related info as member variables,
    to avoid having to pass them around explicitly.
    """

    def __init__(self,
                 expectation_type: ExpectationType,
                 quantifier: Quantifier,
                 matcher_on_existing_regular_file: StringMatcherValue,
                 environment: Environment,
                 files_source_model: FilesMatcherModel,
                 ):
        self.expectation_type = expectation_type
        self.quantifier = quantifier
        self.files_source_model = files_source_model

        pre = environment.path_resolving_environment
        self.path_resolving_environment = pre

        self.matcher_on_existing_regular_file = (matcher_on_existing_regular_file
                                                 .value_of_any_dependency(pre.home_and_sds))
        self.environment = environment
        self.error_reporting = _ErrorReportingHelper(expectation_type,
                                                     files_source_model,
                                                     quantifier)
        self.is_existing_regular_file_checker = FileSystemElementPropertiesMatcher(
            file_properties.ActualFilePropertiesResolver(file_properties.FileType.REGULAR,
                                                         follow_symlinks=True)
        )
        self.models_factory = _ModelsFactory(environment)

    def check(self) -> Optional[ErrorMessageResolver]:
        if self.quantifier is Quantifier.ALL:
            if self.expectation_type is ExpectationType.POSITIVE:
                return self.check__all__positive()
            else:
                return self.check__all__negative()
        else:
            if self.expectation_type is ExpectationType.POSITIVE:
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

    def resolved_actual_file_iter(self) -> Iterator[FileModel]:
        return self.files_source_model.files()

    def check_file(self, file_element: FileModel) -> Optional[ErrorMessageResolver]:
        mb_error = self.is_existing_regular_file_checker.matches(
            self.models_factory.file_system_element_reference(file_element))
        if mb_error is not None:
            raise HardErrorException(mb_error)

        return self.matcher_on_existing_regular_file.matches(self.models_factory.file_to_check(file_element))


class _ModelsFactory:
    def __init__(self, environment: Environment):
        self._id_trans = IdentityStringTransformer()
        self._tmp_file_space = environment.tmp_files_space
        self._destination_file_path_getter = DestinationFilePathGetter()

    def file_to_check(self, file_element: FileModel) -> FileToCheck:
        return FileToCheck(file_element.path,
                           _FilePropertyDescriptorConstructorForFileInDir(file_element),
                           self._tmp_file_space,
                           self._id_trans,
                           self._destination_file_path_getter)

    def file_system_element_reference(self, file_element: FileModel) -> FileSystemElementReference:
        return FileSystemElementReference(
            file_ref_resolvers.constant(file_element.relative_to_root_dir_as_path_value),
            file_element.path
        )


class _ErrorReportingHelper:
    def __init__(self,
                 expectation_type: ExpectationType,
                 files_source_model: FilesMatcherModel,
                 quantifier: Quantifier,
                 ):
        self.files_source_model = files_source_model
        self.expectation_type = expectation_type
        self.quantifier = quantifier
        self._destination_file_path_getter = DestinationFilePathGetter()

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
                                file_element: FileModel) -> ErrorMessageResolver:
        def resolve(environment: ErrorMessageResolvingEnvironment) -> str:
            failing_file_description_lines = path_description.lines_for_path_value(
                file_element.relative_to_root_dir_as_path_value,
                environment.tcds,
            )
            actual_info = diff_msg.ActualInfo(single_line_value, failing_file_description_lines)
            return self._diff_failure_info_for_dir().resolve(environment,
                                                             actual_info).error_message()

        return ErrorMessageResolverFromFunction(resolve)

    def _diff_failure_info_for_dir(self) -> diff_msg_utils.DiffFailureInfoResolver:
        file_property_name = property_description.file_property_name(actual_file_attributes.CONTENTS_ATTRIBUTE,
                                                                     actual_file_attributes.PLAIN_DIR_OBJECT_NAME)
        property_descriptor = self.files_source_model.error_message_info.property_descriptor(
            file_property_name)
        return diff_msg_utils.DiffFailureInfoResolver(
            property_descriptor,
            self.expectation_type,
            diff_msg_utils.ConstantExpectedValueResolver(self._description_of_expected()),
        )

    def _description_of_expected(self):
        return ' '.join([instruction_arguments.QUANTIFIER_ARGUMENTS[self.quantifier],
                         config.QUANTIFICATION_OVER_FILE_ARGUMENT,
                         'satisfies',
                         syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.singular_name])


class _FilePropertyDescriptorConstructorForFileInDir(FilePropertyDescriptorConstructor):
    def __init__(self, file_in_dir: FileModel):
        self._path = file_in_dir

    def construct_for_contents_attribute(self,
                                         contents_attribute: str) -> PropertyDescriptor:
        path_resolver = file_ref_resolvers.constant(self._path.relative_to_root_dir_as_path_value)
        return path_description.path_value_description(
            property_description.file_property_name(contents_attribute,
                                                    actual_file_attributes.PLAIN_FILE_OBJECT_NAME),
            path_resolver)
