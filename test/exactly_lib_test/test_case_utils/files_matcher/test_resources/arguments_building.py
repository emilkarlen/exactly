from abc import ABC, abstractmethod
from typing import Sequence, Dict

from exactly_lib.definitions import instruction_arguments
from exactly_lib.symbol.resolver_structure import SymbolValueResolver
from exactly_lib.symbol.symbol_usage import SymbolUsage
from exactly_lib.test_case_utils.file_or_dir_contents_resources import EMPTINESS_CHECK_ARGUMENT
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.files_matcher import config
from exactly_lib.util.logic_types import Quantifier, ExpectationType
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolsArrAndExpectSetup
from exactly_lib_test.test_case_utils.file_matcher.test_resources.argument_syntax import \
    selection_arguments_for_matcher, file_matcher_arguments
from exactly_lib_test.test_case_utils.string_matcher.parse.test_resources import arguments_building
from exactly_lib_test.test_case_utils.test_resources.negation_argument_handling import ExpectationTypeConfig
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class AssertionVariantArgumentsConstructor:
    """"
    Constructs a string for the arguments that are specific for one of the assertion variants:
    - empty
    - num-files

    Argument string is constructed by __str__
    """

    def __str__(self):
        raise NotImplementedError('abstract method')


class EmptyAssertionVariant(AssertionVariantArgumentsConstructor):
    def __str__(self):
        return EMPTINESS_CHECK_ARGUMENT


class SymbolReferenceAssertionVariant(AssertionVariantArgumentsConstructor):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    def __str__(self):
        return self.symbol_name


class NumFilesAssertionVariant(AssertionVariantArgumentsConstructor):
    def __init__(self,
                 condition: str):
        self._condition = condition

    def __str__(self):
        return '{num_files} {condition}'.format(
            num_files=config.NUM_FILES_CHECK_ARGUMENT,
            condition=self._condition)


class FilesContentsAssertionVariant(AssertionVariantArgumentsConstructor):
    def __init__(self,
                 quantifier: Quantifier,
                 file_contents_assertion: arguments_building.ImplicitActualFileArgumentsConstructor,
                 contents_argument_expectation_type: ExpectationType = ExpectationType.POSITIVE):
        self._quantifier = quantifier
        self._file_contents_assertion = file_contents_assertion
        self._contents_argument_expectation_type = contents_argument_expectation_type

    def __str__(self):
        return '{quantifier} {file} {separator} {contents_assertion}'.format(
            quantifier=instruction_arguments.QUANTIFIER_ARGUMENTS[self._quantifier],
            file=config.QUANTIFICATION_OVER_FILE_ARGUMENT,
            separator=instruction_arguments.QUANTIFICATION_SEPARATOR_ARGUMENT,
            contents_assertion=self._file_contents_assertion.apply(self._contents_argument_expectation_type))


class SubSetSelectionArgumentConstructor:
    def __init__(self, file_matcher: str = ''):
        self._file_matcher = file_matcher

    def apply(self) -> str:
        if self._file_matcher:
            return selection_arguments_for_matcher(self._file_matcher)
        else:
            return ''


def no_selection() -> SubSetSelectionArgumentConstructor:
    return SubSetSelectionArgumentConstructor('')


class FilesMatcherArgumentsConstructor(ABC):
    """
    Constructs a string for "complete" instruction arguments - common arguments
    followed by arguments for an assertion variant.
    """

    @abstractmethod
    def apply(self, etc: ExpectationTypeConfig) -> str:
        pass


class FilesMatcherArgumentsConstructorFromComponents(FilesMatcherArgumentsConstructor):
    def __init__(self,
                 selection_arguments: SubSetSelectionArgumentConstructor,
                 assertion_variant: AssertionVariantArgumentsConstructor,
                 ):
        self._selection_arguments = selection_arguments
        self._assertion_variant = assertion_variant

    def apply(self, etc: ExpectationTypeConfig) -> str:
        return '{selection} {negation} {assertion_variant}'.format(
            selection=self._selection_arguments.apply(),
            negation=etc.nothing__if_positive__not_option__if_negative,
            assertion_variant=str(self._assertion_variant))


def matcher_with_selection_options(assertion_variant: AssertionVariantArgumentsConstructor,
                                   name_option_pattern: str = '',
                                   type_matcher: FileType = None,
                                   named_matcher: str = '',
                                   ) -> FilesMatcherArgumentsConstructor:
    file_matcher = file_matcher_arguments(name_option_pattern,
                                          type_matcher,
                                          named_matcher)

    return FilesMatcherArgumentsConstructorFromComponents(
        SubSetSelectionArgumentConstructor(file_matcher),
        assertion_variant,
    )


def argument_constructor_for_emptiness_check(name_option_pattern: str = '',
                                             type_matcher: FileType = None,
                                             named_matcher: str = '',
                                             ) -> FilesMatcherArgumentsConstructor:
    return matcher_with_selection_options(
        EmptyAssertionVariant(),
        name_option_pattern=name_option_pattern,
        type_matcher=type_matcher,
        named_matcher=named_matcher,
    )


def argument_constructor_for_num_files_check(int_condition: str,
                                             name_option_pattern: str = '',
                                             type_matcher: FileType = None,
                                             named_matcher: str = '',
                                             ) -> FilesMatcherArgumentsConstructor:
    return matcher_with_selection_options(
        NumFilesAssertionVariant(int_condition),
        name_option_pattern=name_option_pattern,
        type_matcher=type_matcher,
        named_matcher=named_matcher,
    )


def argument_constructor_for_symbol_reference(files_matcher_symbol_name: str,
                                              name_option_pattern: str = '',
                                              type_matcher: FileType = None,
                                              named_matcher: str = '',
                                              ) -> FilesMatcherArgumentsConstructor:
    return matcher_with_selection_options(
        SymbolReferenceAssertionVariant(files_matcher_symbol_name),
        name_option_pattern=name_option_pattern,
        type_matcher=type_matcher,
        named_matcher=named_matcher,
    )


class FilesMatcherArgumentsSetup(SymbolsArrAndExpectSetup):
    def __init__(self,
                 arguments: AssertionVariantArgumentsConstructor,
                 symbols_in_arrangement: Dict[str, SymbolValueResolver],
                 expected_references: Sequence[ValueAssertion[SymbolUsage]] = ()):
        super().__init__(symbols_in_arrangement,
                         expected_references)
        self.arguments = arguments


def files_matcher_setup_without_references(arguments: AssertionVariantArgumentsConstructor
                                           ) -> FilesMatcherArgumentsSetup:
    return FilesMatcherArgumentsSetup(arguments, {})
