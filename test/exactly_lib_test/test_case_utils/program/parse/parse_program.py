import sys
import unittest
from typing import Sequence, List, Callable

from exactly_lib.symbol.data import string_sdvs
from exactly_lib.test_case_file_structure.path_relativity import RelHdsOptionType
from exactly_lib.test_case_utils.program.parse import parse_program as sut
from exactly_lib.type_system.data import paths
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.logic.test_resources.string_transformer.symbol_context import \
    StringTransformerPrimitiveSymbolContext
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case.test_resources import command_assertions as asrt_command
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_wo_tcds, ParseExpectation, \
    Expectation, Arrangement, AssertionResolvingEnvironment, prim_asrt__constant, arrangement_w_tcds
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants_for_consume_until_end_of_last_line2, \
    equivalent_source_variants__with_source_check__for_expression_parser_2
from exactly_lib_test.test_case_utils.program.parse import parse_system_program
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as pgm_args, program_sdvs
from exactly_lib_test.test_case_utils.program.test_resources import integration_check
from exactly_lib_test.test_case_utils.test_resources import arguments_building as ab
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_resources.arguments_building import ArgumentElementsRenderer
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
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
                 expected_command: Callable[[AssertionResolvingEnvironment], ValueAssertion[Command]],
                 symbols: Sequence[SymbolContext] = (),
                 mk_arrangement: Callable[[SymbolTable], Arrangement] =
                 lambda sym_tbl: arrangement_wo_tcds(symbols=sym_tbl),
                 ):
        self.name = name
        self.command_renderer = command_renderer
        self.symbols = symbols
        self.expected_command = expected_command
        self.mk_arrangement = mk_arrangement


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
                        command_case.mk_arrangement(SymbolContext.symbol_table_of_contexts(command_case.symbols)),
                        Expectation(
                            ParseExpectation(
                                source=source_case.expected_value,
                                symbol_references=SymbolContext.references_assertion_of_contexts(command_case.symbols),
                            ),
                            primitive=lambda env: (
                                asrt_pgm_val.matches_program(
                                    command_case.expected_command(env),
                                    stdin=asrt_pgm_val.no_stdin(),
                                    transformer=asrt_str_trans.is_identity_transformer(True),
                                )
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
                        command_case.mk_arrangement(SymbolContext.symbol_table_of_contexts(symbols)),
                        Expectation(
                            ParseExpectation(
                                source=source_case.expected,
                                symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                            ),
                            primitive=lambda env: (
                                asrt_pgm_val.matches_program(
                                    command_case.expected_command(env),
                                    stdin=asrt_pgm_val.no_stdin(),
                                    transformer=asrt.is_(transformer.primitive),
                                )
                            )
                        )
                    )


def _single_line_command_cases() -> List[Case]:
    shell_command_line = 'the shell command line'
    system_program = 'the-system-program'
    py_executable_ddv = paths.absolute_file_name(sys.executable)

    executable_file = fs.executable_file('executable-file', '')
    exe_file_relativity = rel_opt.conf_rel_hds(RelHdsOptionType.REL_HDS_CASE)
    executable_file_ddv = paths.of_rel_option(exe_file_relativity.relativity,
                                              paths.constant_path_part(executable_file.name)
                                              )

    program_sdv = program_sdvs.system_program(string_sdvs.str_constant(system_program))

    program_symbol = ProgramSymbolContext.of_sdv('PROGRAM_SYMBOL', program_sdv)

    return [
        Case(
            'executable file',
            command_renderer=pgm_args.executable_file_command_line(
                exe_file_relativity.named_file_conf(executable_file.name).cl_argument.as_str
            ),
            expected_command=lambda env: (
                asrt_command.equals_executable_file_command(
                    executable_file_ddv.value_of_any_dependency__d(env.tcds),
                    []
                )),
            mk_arrangement=lambda sym_tbl: arrangement_w_tcds(
                symbols=sym_tbl,
                hds_contents=exe_file_relativity.populator_for_relativity_option_root__hds(
                    DirContents([executable_file])
                )
            )
        ),
        Case(
            '-python',
            command_renderer=pgm_args.py_interpreter_command_line(),
            expected_command=lambda env: (
                asrt_command.equals_executable_file_command(
                    py_executable_ddv.value_of_any_dependency__d(env.tcds),
                    []
                )),
        ),
        Case(
            'system program',
            command_renderer=pgm_args.system_program_command_line(system_program),
            expected_command=prim_asrt__constant(
                asrt_command.equals_system_program_command(system_program, [])
            )
        ),
        Case(
            'reference',
            command_renderer=pgm_args.symbol_ref_command_line(program_symbol.name),
            symbols=[program_symbol],
            expected_command=prim_asrt__constant(
                asrt_command.equals_system_program_command(system_program, [])
            ),
        ),
        Case(
            'shell',
            command_renderer=pgm_args.shell_command_line(shell_command_line),
            expected_command=prim_asrt__constant(
                asrt_command.equals_shell_command(shell_command_line, [])
            )
        ),
    ]


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
