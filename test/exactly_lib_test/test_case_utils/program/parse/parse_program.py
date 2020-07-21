import pathlib
import sys
import unittest
from typing import Sequence, List

from exactly_lib.symbol.data import string_sdvs
from exactly_lib.test_case_utils.program.parse import parse_program as sut
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.logic.test_resources.string_transformer.symbol_context import \
    StringTransformerPrimitiveSymbolContext
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case.test_resources import command_assertions as asrt_command
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import Expectation, ParseExpectation, \
    arrangement_wo_tcds
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants_for_consume_until_end_of_last_line2, \
    equivalent_source_variants__with_source_check__for_expression_parser_2
from exactly_lib_test.test_case_utils.program.parse import parse_system_program
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args, program_sdvs
from exactly_lib_test.test_case_utils.program.test_resources import integration_check
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.data.test_resources import described_path
from exactly_lib_test.type_system.logic.string_transformer.test_resources import \
    string_transformer_assertions as asrt_str_trans, string_transformers
from exactly_lib_test.type_system.logic.test_resources import program_assertions as asrt_pgm_val


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParseSystemProgram),
        unittest.makeSuite(TestParse),
    ])


class TestParseSystemProgram(unittest.TestCase):
    def test(self):
        # ARRANGE #
        program_name_case = parse_system_program.ProgramNameCase(
            'constant name',
            source_element='program_name',
            expected_resolved_value='program_name',
            expected_symbol_references=[],
        )
        arguments_case = parse_system_program.ArgumentsCase('single constant argument',
                                                            source_elements=['the_argument'],
                                                            expected_resolved_values=lambda tcds: ['the_argument'],
                                                            expected_symbol_references=[])

        parser = sut.program_parser()
        parse_system_program.check_parsing_of_program(self,
                                                      parser,
                                                      pgm_args.system_program_argument_elements,
                                                      program_name_case,
                                                      arguments_case,
                                                      SymbolTable({}))


class Case:
    def __init__(self,
                 name: str,
                 command_renderer: ArgumentElementsRenderer,
                 expected_command: ValueAssertion[Command],
                 symbols: Sequence[SymbolContext] = ()
                 ):
        self.name = name
        self.command_renderer = command_renderer
        self.symbols = symbols
        self.expected_command = expected_command


class TestParse(unittest.TestCase):
    def test_just_command_line(self):
        # ARRANGE #
        command_cases = _single_line_command_cases()
        for command_case in command_cases:
            for source_case in equivalent_source_variants_for_consume_until_end_of_last_line2(
                    command_case.command_renderer.as_arguments):
                with self.subTest(command=command_case.name,
                                  following_source_variant=source_case.name):
                    # ACT & ASSERT #
                    integration_check.CHECKER_WO_EXECUTION.check(
                        self,
                        source_case.input_value,
                        None,
                        arrangement_wo_tcds(
                            symbols=SymbolContext.symbol_table_of_contexts(command_case.symbols)
                        ),
                        Expectation(
                            ParseExpectation(
                                source=source_case.expected_value,
                                symbol_references=SymbolContext.references_assertion_of_contexts(command_case.symbols),
                            ),
                            primitive=asrt_pgm_val.matches_program(
                                command_case.expected_command,
                                stdin=asrt_pgm_val.no_stdin(),
                                transformer=asrt_str_trans.is_identity_transformer(True),
                            )
                        )
                    )

    def test_command_line_followed_by_transformation_on_following_line(self):
        # ARRANGE #
        command_cases = _single_line_command_cases()

        transformer = StringTransformerPrimitiveSymbolContext(
            'STRING_TRANSFORMER',
            string_transformers.to_uppercase()
        )

        for command_case in command_cases:

            command_followed_by_transformer = pgm_args.program_followed_by_transformation(
                command_case.command_renderer,
                ab.singleton(transformer.name__sym_ref_syntax)

            )
            symbols = list(command_case.symbols) + [transformer]

            for source_case in equivalent_source_variants__with_source_check__for_expression_parser_2(
                    command_followed_by_transformer.as_arguments):
                with self.subTest(command=command_case.name,
                                  following_source_variant=source_case.name):
                    # ACT & ASSERT #
                    integration_check.CHECKER_WO_EXECUTION.check(
                        self,
                        source_case.actual,
                        None,
                        arrangement_wo_tcds(
                            symbols=SymbolContext.symbol_table_of_contexts(symbols)
                        ),
                        Expectation(
                            ParseExpectation(
                                source=source_case.expected,
                                symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                            ),
                            primitive=asrt_pgm_val.matches_program(
                                command_case.expected_command,
                                stdin=asrt_pgm_val.no_stdin(),
                                transformer=asrt.is_(transformer.primitive),
                            )
                        )
                    )


def _single_line_command_cases() -> List[Case]:
    shell_command_line = 'the shell command line'
    system_program = 'the-system-program'
    executable_file = sys.executable
    program_sdv = program_sdvs.system_program(string_sdvs.str_constant(system_program))
    program_symbol = ProgramSymbolContext.of_sdv('PROGRAM_SYMBOL', program_sdv)
    return [
        Case(
            'executable file',
            command_renderer=pgm_args.executable_file_command_line(executable_file),
            expected_command=asrt_command.equals_executable_file_command(
                described_path.new_primitive(pathlib.Path(executable_file)),
                []
            ),
        ),
        Case(
            'system program',
            command_renderer=pgm_args.system_program_command_line(system_program),
            expected_command=asrt_command.equals_system_program_command(system_program, [])
        ),
        Case(
            'reference',
            command_renderer=pgm_args.symbol_ref_command_line(program_symbol.name),
            symbols=[program_symbol],
            expected_command=asrt_command.equals_system_program_command(system_program, []),
        ),
        Case(
            'shell',
            command_renderer=pgm_args.shell_command_line(shell_command_line),
            expected_command=asrt_command.equals_shell_command(shell_command_line, [])
        ),
    ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
