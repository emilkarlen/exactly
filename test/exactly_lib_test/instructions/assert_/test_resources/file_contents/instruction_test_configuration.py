import unittest

from exactly_lib.help_texts import file_ref as file_ref_texts
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.instruction_arguments import WITH_TRANSFORMED_CONTENTS_OPTION_NAME
from exactly_lib.instructions.assert_.utils.file_contents import instruction_options
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.section_element_parsers import InstructionParser
from exactly_lib.test_case_utils.parse import parse_here_doc_or_file_ref
from exactly_lib.util.cli_syntax.option_syntax import option_syntax
from exactly_lib.util.logic_types import ExpectationType
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instr_arg_variant_check.negation_argument_handling import \
    ExpectationTypeConfig
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check import \
    home_and_sds_populators as home_or_sds
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction


class AssertionVariantArgumentsConstructor:
    """"
    Constructs a string for the arguments that are specific for one of the assertion variants:
    - empty
    - num-lines
    - ...

    Argument string is constructed by __str__
    """

    def __str__(self):
        raise NotImplementedError('abstract method')


class CommonArgumentsConstructor:
    """
    Constructs a string for the common arguments used by all assertion variants:
    - [TRANSFORMATION]
    - [NEGATION]
    """

    def __init__(self,
                 file_transformer: str = ''):
        self._file_transformer = file_transformer

    def apply(self, etc: ExpectationTypeConfig) -> str:
        return '{transformation} {negation}'.format(
            transformation=self._empty_if_no_file_transformer_otherwise_selection(),
            negation=etc.nothing__if_positive__not_option__if_negative)

    def _empty_if_no_file_transformer_otherwise_selection(self) -> str:
        if self._file_transformer:
            return option_syntax(WITH_TRANSFORMED_CONTENTS_OPTION_NAME) + ' ' + self._file_transformer
        else:
            return ''


class ContentsArgumentsConstructor:
    """
    Constructs a string for arguments of a contents instruction - common arguments
    followed by arguments for an assertion variant.
    """

    def __init__(self,
                 common_arguments: CommonArgumentsConstructor,
                 assertion_variant: AssertionVariantArgumentsConstructor,
                 ):
        self._common_arguments = common_arguments
        self._assertion_variant = assertion_variant

    def apply(self, etc: ExpectationTypeConfig) -> str:
        return '{common} {assertion_variant}'.format(
            common=self._common_arguments.apply(etc),
            assertion_variant=str(self._assertion_variant))


class EmptyAssertionArgumentsConstructor(AssertionVariantArgumentsConstructor):
    def __str__(self):
        return instruction_options.EMPTY_ARGUMENT


class InstructionTestConfiguration:
    def new_parser(self) -> InstructionParser:
        raise NotImplementedError()

    def arrangement_for_contents(self,
                                 actual_contents: str,
                                 post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                 symbols: SymbolTable = None,
                                 ) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()


class InstructionTestConfigurationForContentsOrEquals(InstructionTestConfiguration):
    def first_line_argument(self, argument_tail: str) -> str:
        raise NotImplementedError()

    def source_for(self, argument_tail: str, following_lines=()) -> ParseSource:
        return remaining_source(self.first_line_argument(argument_tail),
                                following_lines)

    def arrangement_for_contents_from_fun(self,
                                          home_and_sds_2_str,
                                          home_or_sds_contents: home_or_sds.HomeOrSdsPopulator = home_or_sds.empty(),
                                          post_sds_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                                          symbols: SymbolTable = None,
                                          ) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()


class TestWithConfigurationBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, configuration: InstructionTestConfiguration):
        super().__init__(configuration)
        self.configuration = configuration

    def _check(self,
               source: ParseSource,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        instruction_check.check(self, self.configuration.new_parser(), source, arrangement, expectation)

    def _check_single_instruction_line_with_source_variants(self,
                                                            instruction_argument: str,
                                                            arrangement: ArrangementPostAct,
                                                            expectation: Expectation):
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            instruction_check.check(self, self.configuration.new_parser(), source, arrangement, expectation)


class TestWithConfigurationAndNegationArgumentBase(TestWithConfigurationBase):
    def __init__(self,
                 configuration: InstructionTestConfiguration,
                 expectation_type: ExpectationType):
        super().__init__(configuration)
        self.maybe_not = ExpectationTypeConfig(expectation_type)

    def shortDescription(self):
        return (str(type(self)) + ' /\n' +
                str(type(self.configuration)) + ' /\n' +
                str(self.maybe_not)
                )


def suite_for__conf__not_argument(configuration: InstructionTestConfiguration,
                                  test_cases: list) -> unittest.TestSuite:
    return unittest.TestSuite(
        [tc(configuration, ExpectationType.POSITIVE) for tc in test_cases] +
        [tc(configuration, ExpectationType.NEGATIVE) for tc in test_cases])


def args(arg_str: str, **kwargs) -> str:
    if kwargs:
        format_map = dict(list(_FORMAT_MAP.items()) + list(kwargs.items()))
        return arg_str.format_map(format_map)
    return arg_str.format_map(_FORMAT_MAP)


_FORMAT_MAP = {
    'any': instruction_arguments.EXISTS_QUANTIFIER_ARGUMENT,
    'every': instruction_arguments.ALL_QUANTIFIER_ARGUMENT,
    'line_matches': instruction_options.LINE_ARGUMENT + ' ' + instruction_options.MATCHES_ARGUMENT,
    'empty': instruction_options.EMPTY_ARGUMENT,
    'equals': instruction_options.EQUALS_ARGUMENT,
    'file_option': option_syntax(parse_here_doc_or_file_ref.FILE_ARGUMENT_OPTION),
    'not': instruction_options.NOT_ARGUMENT,
    'transform_option': option_syntax(WITH_TRANSFORMED_CONTENTS_OPTION_NAME),
    'rel_home_case_option': file_ref_texts.REL_HOME_CASE_OPTION,
    'rel_cwd_option': file_ref_texts.REL_CWD_OPTION,
    'rel_tmp_option': file_ref_texts.REL_TMP_OPTION,
    'rel_symbol_option': file_ref_texts.REL_symbol_OPTION,
}
