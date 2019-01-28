from typing import List, Set, Optional

from exactly_lib.definitions import actual_file_attributes
from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case.pre_or_post_value_validators import ValueValidatorFromResolverValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_system_element_matcher import ErrorMessageResolverForFailingFileProperties2
from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.type_system.logic import string_matcher
from exactly_lib.type_system.logic import string_transformer
from exactly_lib.type_system.logic.file_matcher import FileMatcherValue, FileMatcher, FileMatcherModel
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.util.symbol_table import SymbolTable


class RegularFileMatchesStringMatcher(FileMatcher):
    def __init__(self, string_matcher: string_matcher.StringMatcher):
        self._string_matcher = string_matcher
        self._expected_file_type = file_properties.FileType.REGULAR
        self._is_regular_file_check = file_properties.ActualFilePropertiesResolver(self._expected_file_type,
                                                                                   follow_symlinks=True)

    @property
    def option_description(self) -> str:
        return 'contents matches STRING-MATCHER'

    def matches(self, model: FileMatcherModel) -> bool:
        return self.matches2(model) is None

    def matches2(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
        self._hard_error_if_not_regular_file(model)
        model = self._string_matcher_model(model)
        return self._string_matcher.matches(model)

    def _hard_error_if_not_regular_file(self, model: FileMatcherModel):
        failure_info_properties = self._is_regular_file_check.resolve_failure_info(model.path)
        if failure_info_properties:
            property_descriptor = model.file_descriptor.construct_for_contents_attribute(
                actual_file_attributes.TYPE_ATTRIBUTE
            )
            raise HardErrorException(
                ErrorMessageResolverForFailingFileProperties2(property_descriptor,
                                                              failure_info_properties,
                                                              self._expected_file_type)
            )

    @staticmethod
    def _string_matcher_model(model: FileMatcherModel) -> string_matcher.FileToCheck:
        return string_matcher.FileToCheck(
            model.path,
            model.file_descriptor,
            model.tmp_file_space,
            string_transformer.IdentityStringTransformer(),
            string_matcher.DestinationFilePathGetter(),
        )


class RegularFileMatchesStringMatcherValue(FileMatcherValue):
    def __init__(self,
                 string_matcher: string_matcher.StringMatcherValue,
                 validator: PreOrPostSdsValueValidator):
        self._string_matcher = string_matcher
        self._validator = validator

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._string_matcher.resolving_dependencies()

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._validator

    def value_when_no_dir_dependencies(self) -> FileMatcher:
        return RegularFileMatchesStringMatcher(self._string_matcher.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, tcds: HomeAndSds) -> FileMatcher:
        return RegularFileMatchesStringMatcher(self._string_matcher.value_of_any_dependency(tcds))


class RegularFileMatchesStringMatcherResolver(FileMatcherResolver):
    def __init__(self, string_matcher: StringMatcherResolver):
        self._string_matcher = string_matcher

    @property
    def references(self) -> List[SymbolReference]:
        return self._string_matcher.references

    def resolve(self, symbols: SymbolTable) -> FileMatcherValue:
        return RegularFileMatchesStringMatcherValue(
            self._string_matcher.resolve(symbols),
            ValueValidatorFromResolverValidator(
                symbols,
                self._string_matcher.validator
            )
        )
