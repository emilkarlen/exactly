import unittest

from exactly_lib.instructions.assert_ import exitcode as sut
from exactly_lib.named_element.named_element_usage import NamedElementReference
from exactly_lib.named_element.symbol.restrictions.reference_restrictions import string_made_up_by_just_strings
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_utils.parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.assert_.test_resources import instruction_check, expression
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation, is_pass
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct, ActResultProducerFromActResult
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants, equivalent_source_variants__with_source_check
from exactly_lib_test.named_element.symbol.test_resources import symbol_utils
from exactly_lib_test.named_element.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.section_document.test_resources.parse_source import is_at_beginning_of_line
from exactly_lib_test.test_case_utils.test_resources import svh_assertions
from exactly_lib_test.test_resources.execution import utils
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.parse import remaining_source


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),

        unittest.makeSuite(TestFailingValidationPreSds),
        unittest.makeSuite(TestFailingValidationPreSdsCausedByCustomValidation),
        unittest.makeSuite(TestConstantArguments),
        unittest.makeSuite(TestArgumentWithSymbolReferences),

        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestParse(unittest.TestCase):
    def test_invalid_syntax(self):
        test_cases = [
            ' <> 1',
            '',
            'a b c',
        ]
        parser = sut.Parser()
        for instruction_argument in test_cases:
            with self.subTest(msg=instruction_argument):
                for source in equivalent_source_variants(self, instruction_argument):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        parser.parse(source)

    def test_valid_syntax(self):
        parser = sut.Parser()
        actual_instruction = parser.parse(remaining_source('1'))
        self.assertIsInstance(actual_instruction,
                              AssertPhaseInstruction)


class TestBase(instruction_check.TestCaseBase):
    def _run(self,
             source: ParseSource,
             arrangement: ArrangementPostAct,
             expectation: Expectation):
        self._check(sut.Parser(), source, arrangement, expectation)


class TheInstructionArgumentsVariantConstructor(expression.InstructionArgumentsVariantConstructor):
    """
    Constructs the instruction argument for a given comparision condition string.
    """

    def apply(self,
              condition_str: str,
              ) -> str:
        return condition_str


class TestFailingValidationPreSds(expression.TestFailingValidationPreSdsAbstract):
    def _conf(self) -> expression.Configuration:
        return expression.Configuration(sut.Parser(),
                                        TheInstructionArgumentsVariantConstructor())


class TestFailingValidationPreSdsCausedByCustomValidation(TestBase):
    def test_fail_WHEN_integer_operand_is_not_a_byte(self):
        cases = [
            '-1',
            '256',
        ]
        for invalid_value in cases:
            with self.subTest(invalid_value=invalid_value):
                self._run(
                    remaining_source(invalid_value,
                                     ['following line']),
                    ArrangementPostAct(),
                    Expectation(
                        validation_pre_sds=svh_assertions.is_validation_error(),
                    ),
                )


class TestArgumentWithSymbolReferences(TestBase):
    def test_with_symbol_references(self):
        symbol_1_name = 'symbol_1_name'
        symbol_2_name = 'symbol_2_name'

        test_cases = [
            CaseWithSymbols(
                'single argument form with a symbol that is a single integer',
                argument='{}'.format(symbol_reference_syntax_for_name(symbol_1_name)),
                symbol_name_and_value_list=[NameAndValue(symbol_1_name, '72')],
                actual_value_for_pass=72,
                actual_value_for_fail=87,
            ),
            CaseWithSymbols(
                'single argument form with a symbol that is the last digit of expected value',
                argument='7{}'.format(symbol_reference_syntax_for_name(symbol_1_name)),
                symbol_name_and_value_list=[NameAndValue(symbol_1_name, '2')],
                actual_value_for_pass=72,
                actual_value_for_fail=87,
            ),
            CaseWithSymbols(
                'two argument form with a symbol that is a single integer',
                argument=' = {}'.format(symbol_reference_syntax_for_name(symbol_1_name)),
                symbol_name_and_value_list=[NameAndValue(symbol_1_name, '72')],
                actual_value_for_pass=72,
                actual_value_for_fail=87,
            ),
            CaseWithSymbols(
                'two argument form with two symbols that makes up the expected value when concatenated',
                argument=' = {}{}'.format(
                    symbol_reference_syntax_for_name(symbol_1_name),
                    symbol_reference_syntax_for_name(symbol_2_name)),
                symbol_name_and_value_list=[NameAndValue(symbol_1_name, '7'),
                                            NameAndValue(symbol_2_name, '2')],
                actual_value_for_pass=72,
                actual_value_for_fail=87,
            ),
        ]
        for case in test_cases:
            for sub_name, actual_value, result_expectation in [('pass',
                                                                case.actual_value_for_pass,
                                                                pfh_check.is_pass()),
                                                               ('fail',
                                                                case.actual_value_for_fail,
                                                                pfh_check.is_fail())]:
                with self.subTest(name=case.name, sub_name=sub_name):
                    self._run(
                        remaining_source(case.argument,
                                         ['following line']),
                        ArrangementPostAct(
                            act_result_producer=act_result_of(actual_value),
                            symbols=symbol_table_with_string_constant_symbols(case.symbol_name_and_value_list),
                        ),
                        Expectation(
                            source=is_at_beginning_of_line(2),
                            main_result=result_expectation,
                            symbol_usages=equals_symbol_references(
                                string_symbol_references_of(case.symbol_name_and_value_list))
                        ),
                    )


class TestConstantArguments(TestBase):
    def test_one_argument_for(self):
        test_cases = [
            (_actual_exitcode(0), ' 72 ', _IS_FAIL),
            (_actual_exitcode(72), ' 72 ', _IS_PASS),
        ]
        for arrangement, instr_arg, expectation in test_cases:
            with self.subTest(msg=instr_arg):
                for source in equivalent_source_variants__with_source_check(self, instr_arg):
                    self._run(
                        source,
                        arrangement,
                        expectation,
                    )

    def test_two_argument_form(self):
        test_cases = [
            (_actual_exitcode(0), ' =  72', _IS_FAIL),
            (_actual_exitcode(72), ' =  72', _IS_PASS),

            (_actual_exitcode(72), ' !  72', _IS_FAIL),
            (_actual_exitcode(72), ' !  73', _IS_PASS),

            (_actual_exitcode(72), ' !=  72', _IS_FAIL),
            (_actual_exitcode(72), ' !=  73', _IS_PASS),

            (_actual_exitcode(72), ' <  28', _IS_FAIL),
            (_actual_exitcode(72), ' <  72', _IS_FAIL),
            (_actual_exitcode(72), ' <  87', _IS_PASS),

            (_actual_exitcode(72), ' <= 28', _IS_FAIL),
            (_actual_exitcode(72), ' <= 72', _IS_PASS),
            (_actual_exitcode(72), ' <= 87', _IS_PASS),

            (_actual_exitcode(72), ' > 28', _IS_PASS),
            (_actual_exitcode(72), ' > 72', _IS_FAIL),
            (_actual_exitcode(72), ' > 87', _IS_FAIL),

            (_actual_exitcode(72), ' >= 28', _IS_PASS),
            (_actual_exitcode(72), ' >= 72', _IS_PASS),
            (_actual_exitcode(72), ' >= 87', _IS_FAIL),
        ]
        for arrangement, instr_arg, expectation in test_cases:
            with self.subTest(msg=instr_arg):
                for source in equivalent_source_variants__with_source_check(self, instr_arg):
                    self._run(
                        source,
                        arrangement,
                        expectation,
                    )


class CaseWithSymbols:
    def __init__(self,
                 case_name: str,
                 symbol_name_and_value_list: list,
                 argument: str,
                 actual_value_for_pass: int,
                 actual_value_for_fail: int, ):
        self.name = case_name
        self.argument = argument
        self.actual_value_for_pass = actual_value_for_pass
        self.actual_value_for_fail = actual_value_for_fail
        self.symbol_name_and_value_list = symbol_name_and_value_list


def _actual_exitcode(exit_code: int) -> ArrangementPostAct:
    return ArrangementPostAct(act_result_producer=act_result_of(exit_code))


def act_result_of(exit_code: int):
    return ActResultProducerFromActResult(utils.ActResult(exitcode=exit_code))


def symbol_table_with_string_constant_symbols(symbol_name_and_value_list: list) -> SymbolTable:
    return SymbolTable(dict([(sym.name, symbol_utils.string_constant_container(sym.value))
                             for sym in symbol_name_and_value_list]))


def string_symbol_references_of(symbol_name_and_value_list: list) -> list:
    return [
        NamedElementReference(symbol.name,
                              string_made_up_by_just_strings())
        for symbol in symbol_name_and_value_list
    ]


_IS_PASS = is_pass()
_IS_FAIL = Expectation(main_result=pfh_check.is_fail())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
