import pathlib
from typing import List, Set, Optional

from exactly_lib.symbol.logic.file_matcher import FileMatcherResolver
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case.pre_or_post_value_validators import ValueValidatorFromResolverValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.err_msg.error_info import ErrorMessagePartConstructor
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system.error_message import ConstantErrorMessageResolver, ErrorMessageResolver, \
    FilePropertyDescriptorConstructor, PropertyDescriptor, ErrorMessageResolvingEnvironment
from exactly_lib.type_system.logic import string_matcher
from exactly_lib.type_system.logic import string_transformer
from exactly_lib.type_system.logic.file_matcher import FileMatcherValue, FileMatcher, FileMatcherModel
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.util.symbol_table import SymbolTable


class RegularFileMatchesStringMatcher(FileMatcher):
    def __init__(self, string_matcher: string_matcher.StringMatcher):
        self._string_matcher = string_matcher
        self._expected_file_type = file_properties.TYPE_INFO[FileType.REGULAR]
        self._pathlib_file_type_predicate = self._expected_file_type.pathlib_path_predicate

    def matches(self, model: FileMatcherModel) -> bool:
        if not self._pathlib_file_type_predicate(model.path):
            raise HardErrorException(ConstantErrorMessageResolver('Not a regular file: ' + str(model.path)))
        return False

    @property
    def option_description(self) -> str:
        return 'contents matches STRING-MATCHER'

    def matches(self, model: FileMatcherModel) -> bool:
        return self.matches2(model) is None

    def matches2(self, model: FileMatcherModel) -> Optional[ErrorMessageResolver]:
        self._hard_error_if_not_regular_file(model.path)
        model = self._string_matcher_model(model)
        return self._string_matcher.matches(model)

    def _hard_error_if_not_regular_file(self, path: pathlib.Path):
        if not self._expected_file_type.pathlib_path_predicate(path):
            err_msg = 'Not a {}: {}'.format(self._expected_file_type.description,
                                            path)
            raise HardErrorException(ConstantErrorMessageResolver(err_msg))

    @staticmethod
    def _string_matcher_model(model: FileMatcherModel) -> string_matcher.FileToCheck:
        return string_matcher.FileToCheck(
            model.path,
            _FilePropertyDescriptorConstructor(model.path),
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


class _FilePropertyDescriptorConstructor(FilePropertyDescriptorConstructor):
    def __init__(self, path: pathlib.Path):
        self._path = path

    def construct_for_contents_attribute(self, contents_attribute: str) -> PropertyDescriptor:
        from exactly_lib.test_case_utils.err_msg.property_description import PropertyDescriptorWithConstantPropertyName
        path = self._path

        class _ErrorMessagePartConstructor(ErrorMessagePartConstructor):
            def lines(self, environment: ErrorMessageResolvingEnvironment) -> List[str]:
                return [str(path)]

        return PropertyDescriptorWithConstantPropertyName(contents_attribute,
                                                          _ErrorMessagePartConstructor())
