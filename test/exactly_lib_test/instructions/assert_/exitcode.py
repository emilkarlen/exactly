import unittest
from typing import List

from exactly_lib.instructions.assert_ import exitcode as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_utils.condition import comparators
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.assert_.test_resources import instruction_check, expression
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation, is_pass
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import is_at_beginning_of_line
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case.result.test_resources import pfh_assertions
from exactly_lib_test.test_case.test_resources.act_result import ActResultProducerFromActResult
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants, equivalent_source_variants__with_source_check__consume_last_line
from exactly_lib_test.test_resources.process import SubProcessResult
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),

        unittest.makeSuite(TestFailingValidationPreSds),
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
                        parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_valid_syntax(self):
        parser = sut.Parser()
        actual_instruction = parser.parse(ARBITRARY_FS_LOCATION_INFO,
                                          remaining_source('{op} 1'.format(op=comparators.EQ.name)))
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
        return expression.Configuration(
            sut.Parser(),
            TheInstructionArgumentsVariantConstructor(),
            invalid_integers_according_to_custom_validation=[-1, 256])


class TestArgumentWithSymbolReferences(TestBase):
    def test_with_symbol_references(self):
        symbol_1_name = 'symbol_1_name'
        symbol_2_name = 'symbol_2_name'

        test_cases = [
            CaseWithSymbols(
                'two argument form with a symbol that is a single integer',
                argument=' {op} {sym_ref}'.format(op=comparators.EQ.name,
                                                  sym_ref=symbol_reference_syntax_for_name(symbol_1_name)),
                symbol_name_and_value_list=[NameAndValue(symbol_1_name, '72')],
                actual_value_for_pass=72,
                actual_value_for_fail=87,
            ),
            CaseWithSymbols(
                'two argument form with two symbols that makes up the expected value when concatenated',
                argument=' {op} {sym_ref1}{sym_ref2}'.format(
                    op=comparators.EQ.name,
                    sym_ref1=symbol_reference_syntax_for_name(symbol_1_name),
                    sym_ref2=symbol_reference_syntax_for_name(symbol_2_name)),
                symbol_name_and_value_list=[NameAndValue(symbol_1_name, '7'),
                                            NameAndValue(symbol_2_name, '2')],
                actual_value_for_pass=72,
                actual_value_for_fail=87,
            ),
        ]
        for case in test_cases:
            for sub_name, actual_value, result_expectation in [('pass',
                                                                case.actual_value_for_pass,
                                                                pfh_assertions.is_pass()),
                                                               ('fail',
                                                                case.actual_value_for_fail,
                                                                pfh_assertions.is_fail__with_arbitrary_message())]:
                with self.subTest(name=case.name, sub_name=sub_name):
                    self._run(
                        remaining_source(case.argument,
                                         ['following line']),
                        ArrangementPostAct(
                            act_result_producer=act_result_of(actual_value),
                            symbols=case.symbol_table,
                        ),
                        Expectation(
                            source=is_at_beginning_of_line(2),
                            main_result=result_expectation,
                            symbol_usages=asrt.matches_sequence(
                                case.reference_assertions__string_made_up_of_just_strings)
                        ),
                    )


class TestConstantArguments(TestBase):
    def test_two_argument_form(self):
        test_cases = [
            (_actual_exitcode(0), ' {op}  72', comparators.EQ, _IS_FAIL),
            (_actual_exitcode(72), ' {op}  72', comparators.EQ, _IS_PASS),

            (_actual_exitcode(72), ' ! {op} 72', comparators.EQ, _IS_FAIL),
            (_actual_exitcode(72), ' ! {op} 73', comparators.EQ, _IS_PASS),

            (_actual_exitcode(72), ' {op}  72', comparators.NE, _IS_FAIL),
            (_actual_exitcode(72), ' {op}  73', comparators.NE, _IS_PASS),

            (_actual_exitcode(72), ' {op}  28', comparators.LT, _IS_FAIL),
            (_actual_exitcode(72), ' {op}  72', comparators.LT, _IS_FAIL),
            (_actual_exitcode(72), ' {op}  87', comparators.LT, _IS_PASS),

            (_actual_exitcode(72), ' {op} 28', comparators.LTE, _IS_FAIL),
            (_actual_exitcode(72), ' {op} 72', comparators.LTE, _IS_PASS),
            (_actual_exitcode(72), ' {op} 87', comparators.LTE, _IS_PASS),

            (_actual_exitcode(72), ' {op} 28', comparators.GT, _IS_PASS),
            (_actual_exitcode(72), ' {op} 72', comparators.GT, _IS_FAIL),
            (_actual_exitcode(72), ' {op} 87', comparators.GT, _IS_FAIL),

            (_actual_exitcode(72), ' {op} 28', comparators.GTE, _IS_PASS),
            (_actual_exitcode(72), ' {op} 72', comparators.GTE, _IS_PASS),
            (_actual_exitcode(72), ' {op} 87', comparators.GTE, _IS_FAIL),
        ]
        for arrangement, instr_arg_template, operator, expectation in test_cases:
            instr_arg = instr_arg_template.format(op=operator.name)
            with self.subTest(msg=instr_arg):
                for source in equivalent_source_variants__with_source_check__consume_last_line(self, instr_arg):
                    self._run(
                        source,
                        arrangement,
                        expectation,
                    )


class CaseWithSymbols:
    def __init__(self,
                 case_name: str,
                 symbol_name_and_value_list: List[NameAndValue],
                 argument: str,
                 actual_value_for_pass: int,
                 actual_value_for_fail: int, ):
        self.name = case_name
        self.argument = argument
        self.actual_value_for_pass = actual_value_for_pass
        self.actual_value_for_fail = actual_value_for_fail
        self.symbol_name_and_value_list = symbol_name_and_value_list
        self.symbol_contexts = [
            StringConstantSymbolContext(nav.name, nav.value)
            for nav in symbol_name_and_value_list
        ]

    @property
    def symbol_table(self) -> SymbolTable:
        return SymbolContext.symbol_table_of_contexts(self.symbol_contexts)

    @property
    def reference_assertions__string_made_up_of_just_strings(self) -> List[ValueAssertion[SymbolReference]]:
        return [
            symbol_context.reference_assertion__string_made_up_of_just_strings
            for symbol_context in self.symbol_contexts
        ]


def _actual_exitcode(exit_code: int) -> ArrangementPostAct:
    return ArrangementPostAct(act_result_producer=act_result_of(exit_code))


def act_result_of(exit_code: int):
    return ActResultProducerFromActResult(SubProcessResult(exitcode=exit_code))


_IS_PASS = is_pass()
_IS_FAIL = Expectation(main_result=pfh_assertions.is_fail__with_arbitrary_message())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
