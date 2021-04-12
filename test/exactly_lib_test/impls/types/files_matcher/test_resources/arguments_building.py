from abc import ABC, abstractmethod
from typing import Sequence, List

from exactly_lib.definitions import logic
from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.types.files_matcher import config
from exactly_lib.symbol import symbol_syntax
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.logic_types import Quantifier, ExpectationType
from exactly_lib_test.impls.types.file_matcher.test_resources import argument_building as fm_args
from exactly_lib_test.impls.types.file_matcher.test_resources.argument_syntax import \
    file_matcher_arguments
from exactly_lib_test.impls.types.files_condition.test_resources.arguments_building import FilesConditionArg
from exactly_lib_test.impls.types.test_resources.negation_argument_handling import ExpectationTypeConfig
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolsArrEx
from exactly_lib_test.test_resources import argument_renderer
from exactly_lib_test.test_resources.argument_renderer import FromArgumentElementsBase
from exactly_lib_test.test_resources.arguments.arguments_building import ArgumentElements
from exactly_lib_test.test_resources.matcher_argument import MatcherArgument
from exactly_lib_test.test_resources.strings import WithToString
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


class FilesMatcherArg(MatcherArgument, ABC):
    pass


class SymbolReference(FilesMatcherArg):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    @property
    def elements(self) -> List:
        return [self.symbol_name]


class SymbolReferenceWReferenceSyntax(FilesMatcherArg):
    def __init__(self, symbol_name: str):
        self.symbol_name = symbol_name

    @property
    def elements(self) -> List:
        return [symbol_syntax.symbol_reference_syntax_for_name(self.symbol_name)]


class Empty(FilesMatcherArg):

    @property
    def elements(self) -> List:
        return [config.EMPTINESS_CHECK_ARGUMENT]


class NumFiles(FilesMatcherArg):
    def __init__(self,
                 int_expr: str,
                 int_expr_on_new_line: bool = False,
                 ):
        self.int_expr = int_expr
        self.int_expr_on_new_line = int_expr_on_new_line

    @property
    def elements(self) -> List:
        ret_val = [
            config.NUM_FILES_CHECK_ARGUMENT,
            self.int_expr,
        ]

        if self.int_expr_on_new_line:
            ret_val.insert(1, '\n')

        return ret_val


class Quantification(FilesMatcherArg):
    def __init__(self,
                 quantifier: Quantifier,
                 element_matcher: fm_args.FileMatcherArg,
                 ):
        self.quantifier = quantifier
        self.element_matcher = element_matcher

    @property
    def elements(self) -> List:
        return (
                [
                    logic.QUANTIFIER_ARGUMENTS[self.quantifier],
                    config.QUANTIFICATION_OVER_FILE_ARGUMENT,
                    logic.QUANTIFICATION_SEPARATOR_ARGUMENT,
                ] +
                self.element_matcher.elements
        )


class Selection(FilesMatcherArg):
    def __init__(self,
                 selector: fm_args.FileMatcherArg,
                 on_selection: FilesMatcherArg,
                 ):
        self.selector = selector
        self.on_selection = on_selection

    @property
    def elements(self) -> List:
        return (
                [option_syntax.option_syntax(config.SELECTION_OPTION.name)]
                + self.selector.elements +
                self.on_selection.elements
        )


class Prune(FilesMatcherArg):
    def __init__(self,
                 prune: MatcherArgument,
                 on_resulting_contents: FilesMatcherArg,
                 ):
        self.prune = prune
        self.on_resulting_contents = on_resulting_contents

    @property
    def elements(self) -> List:
        return (
                [option_syntax.option_syntax(config.PRUNE_OPTION.name)]
                + self.prune.elements +
                self.on_resulting_contents.elements
        )


class MatchesFilesCondition(FromArgumentElementsBase, FilesMatcherArg, ABC):
    def __init__(self,
                 full: bool,
                 files_condition: FilesConditionArg):
        self.full = full
        self.files_condition = files_condition

    @property
    def as_argument_elements(self) -> ArgumentElements:
        form_arguments = [config.MATCHES_ARGUMENT]
        if self.full:
            form_arguments.append(option_syntax.option_syntax(config.MATCHES_FULL_OPTION.name))
        return self.files_condition.as_argument_elements.with_first_line_preceded_by(form_arguments)


def matches_non_full(files_condition: FilesConditionArg) -> FilesMatcherArg:
    return MatchesFilesCondition(False, files_condition)


def matches_full(files_condition: FilesConditionArg) -> FilesMatcherArg:
    return MatchesFilesCondition(True, files_condition)


class BinaryOperator(FilesMatcherArg):
    def __init__(self,
                 operator: str,
                 operands: Sequence[FilesMatcherArg]):
        self.operator = operator
        self.operands = operands

    @property
    def elements(self) -> List:
        return argument_renderer.elements_for_binary_operator_arg(self.operator, self.operands)


def conjunction(operands: Sequence[FilesMatcherArg]) -> BinaryOperator:
    return BinaryOperator(logic.AND_OPERATOR_NAME, operands)


def disjunction(operands: Sequence[FilesMatcherArg]) -> BinaryOperator:
    return BinaryOperator(logic.OR_OPERATOR_NAME, operands)


class Custom(FilesMatcherArg):
    def __init__(self, string_matcher: WithToString):
        self.string_matcher = string_matcher

    @property
    def elements(self) -> List:
        return [str(self.string_matcher)]


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
        return config.EMPTINESS_CHECK_ARGUMENT


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


class FileQuantificationAssertionVariant(AssertionVariantArgumentsConstructor):
    def __init__(self,
                 quantifier: Quantifier,
                 file_matcher: fm_args.WithOptionalNegation,
                 file_matcher_expectation_type: ExpectationType = ExpectationType.POSITIVE):
        self._quantifier = quantifier
        self._file_assertion = file_matcher.get(file_matcher_expectation_type)
        self._contents_argument_expectation_type = file_matcher_expectation_type

    def __str__(self):
        return '{quantifier} {file} {separator} {file_assertion}'.format(
            quantifier=logic.QUANTIFIER_ARGUMENTS[self._quantifier],
            file=config.QUANTIFICATION_OVER_FILE_ARGUMENT,
            separator=logic.QUANTIFICATION_SEPARATOR_ARGUMENT,
            file_assertion=str(self._file_assertion)
        )


class SubSetSelectionArgumentConstructor:
    def __init__(self, file_matcher: str = ''):
        self._file_matcher = file_matcher

    def apply(self) -> str:
        if self._file_matcher:
            return selection_arguments_for_matcher(self._file_matcher)
        else:
            return ''

    def __str__(self):
        return self.apply()


def no_selection() -> SubSetSelectionArgumentConstructor:
    return SubSetSelectionArgumentConstructor('')


class FilesMatcherArgumentsConstructor(ABC):
    """
    Constructs a string for "complete" instruction arguments - common arguments
    followed by arguments for an assertion variant.
    """

    @abstractmethod
    def apply(self, etc: ExpectationTypeConfig) -> str:
        raise NotImplementedError('abstract method')


class SelectionAndMatcherArgumentsConstructor(FilesMatcherArgumentsConstructor):
    def __init__(self,
                 selection,
                 files_matcher):
        self.selection = selection
        self.files_matcher = files_matcher

    def apply(self, etc: ExpectationTypeConfig) -> str:
        return '{selection} {expectation_type} {files_matcher}'.format(
            selection=str(SubSetSelectionArgumentConstructor(self.selection)),
            expectation_type=etc.nothing__if_positive__not_option__if_negative,
            files_matcher=str(self.files_matcher)
        )


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


def complete_arguments_constructor(assertion_variant: AssertionVariantArgumentsConstructor,
                                   file_matcher: str = '') -> FilesMatcherArgumentsConstructor:
    return FilesMatcherArgumentsConstructorFromComponents(
        SubSetSelectionArgumentConstructor(file_matcher),
        assertion_variant,
    )


class FilesMatcherArgumentsSetup(SymbolsArrEx):
    def __init__(self,
                 arguments: AssertionVariantArgumentsConstructor,
                 symbols_in_arrangement: List[SymbolContext],
                 expected_references: Sequence[Assertion[SymbolReference]] = ()):
        super().__init__(symbols_in_arrangement,
                         expected_references)
        self.arguments = arguments


def files_matcher_setup_without_references(arguments: AssertionVariantArgumentsConstructor
                                           ) -> FilesMatcherArgumentsSetup:
    return FilesMatcherArgumentsSetup(arguments, [])


def selection_arguments(name_pattern: str = '',
                        type_match: FileType = None,
                        named_matcher: str = '') -> str:
    """
    Gives the CLI argument and options for selection of given
    matchers
    :param name_pattern: Name selector, or nothing, if empty string.
    :param type_match: Type selector, or nothing, if None
    :returns str: Empty string iff no selector is given.
    """
    the_matchers_arguments = file_matcher_arguments(name_pattern,
                                                    type_match,
                                                    named_matcher)
    if the_matchers_arguments:
        return selection_arguments_for_matcher(the_matchers_arguments)
    else:
        return ''


def selection_arguments_for_matcher(matcher: str) -> str:
    return (option_syntax.option_syntax(config.SELECTION_OPTION.name) +
            ' ' +
            matcher)


def symbol_reference(symbol_name: str) -> str:
    return symbol_name


def arbitrary_single_line_value_that_must_not_be_quoted() -> str:
    return config.EMPTINESS_CHECK_ARGUMENT
