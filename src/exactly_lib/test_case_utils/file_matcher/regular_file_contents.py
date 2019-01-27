from typing import List, Set

from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case.pre_or_post_value_validators import ValueValidatorFromResolverValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system.error_message import ConstantErrorMessageResolver
from exactly_lib.type_system.logic.file_matcher import FileMatcherValue, FileMatcher, FileMatcherModel
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.string_matcher import StringMatcherValue, StringMatcher
from exactly_lib.util.symbol_table import SymbolTable


class RegularFileMatchesStringMatcher(FileMatcher):
    def __init__(self, string_matcher: StringMatcher):
        self._string_matcher = string_matcher
        self._pathlib_file_type_predicate = file_properties.TYPE_INFO[FileType.REGULAR].pathlib_path_predicate

    def matches(self, model: FileMatcherModel) -> bool:
        if not self._pathlib_file_type_predicate(model.path):
            raise HardErrorException(ConstantErrorMessageResolver('Not a regular file: ' + str(model.path)))
        return False

    @property
    def option_description(self) -> str:
        return 'contents matches STRING-MATCHER'


class RegularFileMatchesStringMatcherValue(FileMatcherValue):
    def __init__(self,
                 string_matcher: StringMatcherValue,
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
