import contextlib
from typing import Sequence, Optional, Iterator

from exactly_lib.definitions import actual_file_attributes
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.primitives import files_matcher as files_matcher_primitives
from exactly_lib.symbol.logic.file_matcher import FileMatcherSdv
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.err_msg import diff_msg_utils, diff_msg
from exactly_lib.test_case_utils.err_msg import err_msg_resolvers
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.err_msg2 import path_rendering
from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForFileWithDescriptor
from exactly_lib.test_case_utils.files_matcher.impl import files_matchers
from exactly_lib.type_system.data import path_description
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.err_msg.prop_descr import PropertyDescriptor, FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv, FileMatcherModel, FileMatcher
from exactly_lib.type_system.logic.files_matcher import FileModel, FilesMatcherModel, FilesMatcher, \
    FilesMatcherConstructor, FilesMatcherDdv
from exactly_lib.type_system.logic.impls import quantifier_matchers
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult, MatcherWTraceAndNegation
from exactly_lib.type_system.logic.string_matcher import DestinationFilePathGetter, FileToCheck
from exactly_lib.type_system.logic.string_transformer import IdentityStringTransformer
from exactly_lib.util import logic_types
from exactly_lib.util.description_tree.renderer import DetailsRenderer
from exactly_lib.util.file_utils import TmpDirFileSpace
from exactly_lib.util.logic_types import Quantifier, ExpectationType
from exactly_lib.util.symbol_table import SymbolTable

_ONE_FILE_SATISFIES = 'one file match'
_NO_FILE_SATISFY = 'no file match'
_FAILING_FILES_HEADER = 'There are non-matching files:'
_QUANTIFIER__FILE__SATISFY = ' file match'
_SATISFIES = 'matches'


def quantified_matcher(quantifier: Quantifier,
                       matcher_on_file: FileMatcherSdv) -> FilesMatcherSdv:
    return _QuantifiedMatcherSdv(quantifier,
                                 matcher_on_file)


class _QuantifiedMatcher(FilesMatcher):
    def __init__(self,
                 expectation_type: ExpectationType,
                 quantifier: Quantifier,
                 matcher_on_file: FileMatcher,
                 tmp_files_space: TmpDirFileSpace):
        self._expectation_type = expectation_type
        self._quantifier = quantifier
        self._matcher_on_file = matcher_on_file
        self._tmp_files_space = tmp_files_space

    @property
    def name(self) -> str:
        return _NAMES[self._quantifier]

    @property
    def negation(self) -> FilesMatcher:
        return _QuantifiedMatcher(
            logic_types.negation(self._expectation_type),
            self._quantifier,
            self._matcher_on_file,
            self._tmp_files_space,
        )

    def matches_emr(self, files_source: FilesMatcherModel) -> Optional[ErrorMessageResolver]:
        checker = _Checker(self._expectation_type,
                           self._quantifier,
                           self._matcher_on_file,
                           self._tmp_files_space,
                           files_source)
        return checker.check()

    def matches_w_trace(self, model: FilesMatcherModel) -> MatchingResult:
        matcher = self._matcher_w_trace()
        if self._expectation_type is ExpectationType.NEGATIVE:
            matcher = matcher.negation

        return matcher.matches_w_trace(model)

    def _matcher_w_trace(self) -> MatcherWTraceAndNegation[FilesMatcherModel]:
        return (
            quantifier_matchers.ForAll(
                self._element_setup(),
                self._matcher_on_file,
            )
            if self._quantifier is Quantifier.ALL
            else
            quantifier_matchers.Exists(
                self._element_setup(),
                self._matcher_on_file,
            )

        )

    def _element_setup(self) -> quantifier_matchers.ElementSetup:
        return quantifier_matchers.ElementSetup(
            files_matcher_primitives.QUANTIFICATION_OVER_FILE_ARGUMENT,
            syntax_elements.FILE_MATCHER_SYNTAX_ELEMENT.singular_name,
            self._file_elements_from_model,
            _element_detail_renderer,
        )

    @contextlib.contextmanager
    def _file_elements_from_model(self, model: FilesMatcherModel) -> Iterator[FileMatcherModel]:
        model_factory = _ModelsFactory(self._tmp_files_space)
        yield (
            model_factory.file_matcher_model(file_element)
            for file_element in model.files()
        )


class _QuantifiedMatcherDdv(FilesMatcherDdv):
    def __init__(self,
                 quantifier: Quantifier,
                 element_matcher: FileMatcherDdv,
                 ):
        self._quantifier = quantifier
        self._element_matcher = element_matcher

    @property
    def validator(self) -> DdvValidator:
        return self._element_matcher.validator

    def value_of_any_dependency(self, tcds: Tcds) -> FilesMatcherConstructor:
        matcher_on_file = self._element_matcher.value_of_any_dependency(tcds)

        def mk_matcher(tmp_files_space: TmpDirFileSpace) -> FilesMatcher:
            return _QuantifiedMatcher(
                ExpectationType.POSITIVE,
                self._quantifier,
                matcher_on_file,
                tmp_files_space,
            )

        return files_matchers.ConstructorFromFunction(mk_matcher)


class _QuantifiedMatcherSdv(FilesMatcherSdv):
    def __init__(self,
                 quantifier: Quantifier,
                 element_matcher: FileMatcherSdv):
        self._quantifier = quantifier
        self._element_matcher = element_matcher

    @property
    def references(self) -> Sequence[SymbolReference]:
        return self._element_matcher.references

    def resolve(self, symbols: SymbolTable) -> FilesMatcherDdv:
        return _QuantifiedMatcherDdv(
            self._quantifier,
            self._element_matcher.resolve(symbols),
        )


class _Checker:
    """
    Helper that keeps some environment related info as member variables,
    to avoid having to pass them around explicitly.
    """

    def __init__(self,
                 expectation_type: ExpectationType,
                 quantifier: Quantifier,
                 matcher_on_file: FileMatcher,
                 tmp_files_space: TmpDirFileSpace,
                 files_source_model: FilesMatcherModel,
                 ):
        self.expectation_type = expectation_type
        self.quantifier = quantifier
        self.files_source_model = files_source_model

        self.matcher_on_file = matcher_on_file

        self.error_reporting = _ErrorReportingHelper(expectation_type,
                                                     files_source_model,
                                                     quantifier)
        self.models_factory = _ModelsFactory(tmp_files_space)

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
        # REFACT 2019-04-26 [error messages]: Files after 1st non-matching file
        # should be retrieved only when rendering error message.

        failures = []
        for actual_file in self.resolved_actual_file_iter():
            mb_failure = self.check_file(actual_file)
            if mb_failure is not None:
                failures.append(mb_failure)
        return (
            err_msg_resolvers.section(_FAILING_FILES_HEADER,
                                      err_msg_resolvers.itemized_list(failures))
            if failures
            else None
        )

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
        return self.error_reporting.err_msg_for_dir(_NO_FILE_SATISFY)

    def check__exists__negative(self) -> Optional[ErrorMessageResolver]:
        for actual_file in self.resolved_actual_file_iter():
            mb_failure = self.check_file(actual_file)
            if mb_failure is None:
                return self.error_reporting.err_msg_for_file_in_dir(_ONE_FILE_SATISFIES, actual_file)
        return None

    def resolved_actual_file_iter(self) -> Iterator[FileModel]:
        return self.files_source_model.files()

    def check_file(self, file_element: FileModel) -> Optional[ErrorMessageResolver]:
        return self.matcher_on_file.matches_emr(self.models_factory.file_matcher_model(file_element))


class _ModelsFactory:
    def __init__(self, tmp_files_space: TmpDirFileSpace):
        self._id_trans = IdentityStringTransformer()
        self._tmp_file_space = tmp_files_space
        self._destination_file_path_getter = DestinationFilePathGetter()

    def file_to_check(self, file_element: FileModel) -> FileToCheck:
        return FileToCheck(file_element.path,
                           _FilePropertyDescriptorConstructorForFileInDir(file_element),
                           self._tmp_file_space,
                           self._id_trans,
                           self._destination_file_path_getter)

    def file_matcher_model(self, file_element: FileModel) -> FileMatcherModel:
        return FileMatcherModelForFileWithDescriptor(self._tmp_file_space,
                                                     file_element.path,
                                                     _FilePropertyDescriptorConstructorForFileInDir(file_element))


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
        single_line_value = instruction_arguments.QUANTIFIER_ARGUMENTS[self.quantifier] + _QUANTIFIER__FILE__SATISFY
        return self.err_msg_for_dir(single_line_value)

    def err_msg_for_dir(self, single_line_value: str) -> ErrorMessageResolver:
        def resolve() -> str:
            return self._diff_failure_info_for_dir().resolve(diff_msg.ActualInfo(single_line_value)).error_message()

        return err_msg_resolvers.of_function(resolve)

    def err_msg_for_file_in_dir(self,
                                single_line_value: str,
                                file_element: FileModel) -> ErrorMessageResolver:
        def resolve() -> str:
            failing_file_description_lines = path_rendering.path_strings(
                file_element.path.describer,
            )
            actual_info = diff_msg.ActualInfo(single_line_value, failing_file_description_lines)
            return self._diff_failure_info_for_dir().resolve(actual_info).error_message()

        return err_msg_resolvers.of_function(resolve)

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
                         files_matcher_primitives.QUANTIFICATION_OVER_FILE_ARGUMENT,
                         _SATISFIES,
                         syntax_elements.STRING_MATCHER_SYNTAX_ELEMENT.singular_name])


class _FilePropertyDescriptorConstructorForFileInDir(FilePropertyDescriptorConstructor):
    def __init__(self, file_in_dir: FileModel):
        self._file_in_dir = file_in_dir

    def construct_for_contents_attribute(self,
                                         contents_attribute: str) -> PropertyDescriptor:
        return path_description.path_value_description(
            property_description.file_property_name(contents_attribute,
                                                    actual_file_attributes.PLAIN_FILE_OBJECT_NAME),
            self._file_in_dir.path.describer,
            True,
        )


def _element_detail_renderer(element: FileMatcherModel) -> DetailsRenderer:
    return custom_details.PathValueDetailsRenderer(element.path.describer)


_NAMES = {
    q: ' '.join([
        instruction_arguments.QUANTIFIER_ARGUMENTS[q],
        files_matcher_primitives.QUANTIFICATION_OVER_FILE_ARGUMENT,
    ])
    for q in Quantifier
}
