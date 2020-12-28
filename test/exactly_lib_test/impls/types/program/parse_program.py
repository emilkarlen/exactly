import sys
import unittest
from typing import Sequence, List, Callable

from exactly_lib.impls.types.program.parse import parse_program
from exactly_lib.impls.types.string_transformer import names
from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_prims.program.command import CommandDriver
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.logic.test_resources.integration_check import IntegrationChecker
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_wo_tcds, ParseExpectation, \
    Expectation, Arrangement, AssertionResolvingEnvironment, prim_asrt__constant, arrangement_w_tcds
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants_for_consume_until_end_of_last_line2, \
    equivalent_source_variants__with_source_check__for_expression_parser_2
from exactly_lib_test.impls.types.program.test_resources import arguments_building as pgm_args, program_sdvs, \
    integration_check_config
from exactly_lib_test.impls.types.program.test_resources import integration_check_applier
from exactly_lib_test.impls.types.test_resources import arguments_building as ab
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import file_assertions as asrt_path
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerPrimitiveSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command, \
    program_assertions as asrt_pgm_val
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers, \
    string_transformer_assertions as asrt_str_trans
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestWithoutExecution)


class Case:
    def __init__(self,
                 name: str,
                 command_renderer: ArgumentElementsRenderer,
                 expected_command: Callable[[AssertionResolvingEnvironment], ValueAssertion[CommandDriver]],
                 symbols: Sequence[SymbolContext] = (),
                 mk_arrangement: Callable[[SymbolTable], Arrangement] =
                 lambda sym_tbl: arrangement_wo_tcds(symbols=sym_tbl),
                 ):
        self.name = name
        self.command_renderer = command_renderer
        self.symbols = symbols
        self.expected_command = expected_command
        self.mk_arrangement = mk_arrangement


class TestWithoutExecution(unittest.TestCase):
    def test_just_command_line(self):
        # ARRANGE #
        command_cases = _single_line_command_cases()
        for command_case in command_cases:
            for source_case in equivalent_source_variants_for_consume_until_end_of_last_line2(
                    command_case.command_renderer.as_arguments):
                with self.subTest(command=command_case.name,
                                  following_source_variant=source_case.name):
                    # ACT & ASSERT #
                    CHECKER_WO_EXECUTION.check(
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
                                    asrt_command.matches_command(
                                        driver=command_case.expected_command(env),
                                        arguments=asrt.is_empty_sequence
                                    ),
                                    stdin=asrt_pgm_val.no_stdin(),
                                    transformer=asrt_str_trans.is_identity_transformer(True),
                                )
                            )
                        )
                    )

    def test_arguments(self):
        arg_wo_space = 'arg_wo_space'
        arg_w_space = 'an arg w space'
        arg_w_space__src = surrounded_by_soft_quotes(arg_w_space)
        arguments_cases = [
            NIE(
                'one',
                input_value=ArgumentElements([arg_w_space__src]),
                expected_value=[arg_w_space],
            ),
            NIE(
                'two',
                input_value=ArgumentElements([arg_wo_space, arg_w_space__src]),
                expected_value=[arg_wo_space, arg_w_space],
            ),
        ]
        # ARRANGE #
        command_cases = _single_line_command_cases__w_argument_list()
        for command_case in command_cases:
            for arguments_case in arguments_cases:
                arguments = (
                    command_case.command_renderer.as_argument_elements
                        .followed_by(arguments_case.input_value)
                        .as_arguments
                )
                expected_arguments = asrt.matches_sequence([
                    asrt.equals(arg)
                    for arg in arguments_case.expected_value
                ])
                for source_case in equivalent_source_variants_for_consume_until_end_of_last_line2(arguments):
                    with self.subTest(command=command_case.name,
                                      arguments=arguments_case.name,
                                      following_source_variant=source_case.name):
                        # ACT & ASSERT #
                        CHECKER_WO_EXECUTION.check(
                            self,
                            source_case.input_value,
                            None,
                            command_case.mk_arrangement(SymbolContext.symbol_table_of_contexts(command_case.symbols)),
                            Expectation(
                                ParseExpectation(
                                    source=source_case.expected_value,
                                    symbol_references=SymbolContext.references_assertion_of_contexts(
                                        command_case.symbols),
                                ),
                                primitive=lambda env: (
                                    asrt_pgm_val.matches_program(
                                        asrt_command.matches_command(
                                            driver=command_case.expected_command(env),
                                            arguments=expected_arguments
                                        ),
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
                    CHECKER_WO_EXECUTION.check(
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
                                    asrt_command.matches_command(
                                        driver=command_case.expected_command(env),
                                        arguments=asrt.is_empty_sequence
                                    ),
                                    stdin=asrt_pgm_val.no_stdin(),
                                    transformer=asrt.is_(transformer.primitive),
                                )
                            )
                        )
                    )

    def test_string_transformer_should_be_parsed_as_simple_expression(self):
        # ARRANGE #
        transformer = StringTransformerPrimitiveSymbolContext(
            'STRING_TRANSFORMER',
            string_transformers.to_uppercase()
        )
        after_bin_op = 'after bin op'
        string_transformer_argument = ab.binary_operator(
            names.SEQUENCE_OPERATOR_NAME,
            [
                ab.symbol_reference(transformer.name),
                ab.singleton(after_bin_op),
            ],
        )
        expected_source_after_parse = asrt_source.is_at_line(
            current_line_number=2,
            remaining_part_of_current_line=string_transformer_argument.operator + ' ' + after_bin_op,
        )
        for command_case in _single_line_command_cases():
            command_followed_by_transformer = pgm_args.program_followed_by_transformation(
                command_case.command_renderer,
                string_transformer_argument,
            )
            symbols = list(command_case.symbols) + [transformer]

            with self.subTest(command=command_case.name):
                source = command_followed_by_transformer.as_remaining_source
                # ACT & ASSERT #
                CHECKER_WO_EXECUTION.check(
                    self,
                    source,
                    None,
                    command_case.mk_arrangement(SymbolContext.symbol_table_of_contexts(symbols)),
                    Expectation(
                        ParseExpectation(
                            source=expected_source_after_parse,
                            symbol_references=SymbolContext.references_assertion_of_contexts(symbols),
                        ),
                        primitive=lambda env: (
                            asrt_pgm_val.matches_program(
                                asrt_command.matches_command(
                                    driver=command_case.expected_command(env),
                                    arguments=asrt.is_empty_sequence
                                ),
                                stdin=asrt_pgm_val.no_stdin(),
                                transformer=asrt.is_(transformer.primitive),
                            )
                        )
                    )
                )


def _single_line_command_cases__w_argument_list() -> List[Case]:
    executable_file = fs.executable_file('executable-file', '')
    exe_file_relativity = rel_opt.conf_rel_hds(RelHdsOptionType.REL_HDS_CASE)
    executable_file_ddv = path_ddvs.of_rel_option(exe_file_relativity.relativity,
                                                  path_ddvs.constant_path_part(executable_file.name)
                                                  )

    system_program = 'the-system-program'
    program_sdv = program_sdvs.system_program(string_sdvs.str_constant(system_program))
    program_symbol = ProgramSymbolContext.of_sdv('PROGRAM_SYMBOL', program_sdv)

    return [
        Case(
            'executable file',
            command_renderer=pgm_args.executable_file_command_line(
                exe_file_relativity.named_file_conf(executable_file.name).cl_argument.as_str
            ),
            expected_command=lambda env: (
                asrt_command.matches_executable_file_command_driver(
                    asrt.equals(executable_file_ddv.value_of_any_dependency__d(env.tcds).primitive),
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
            expected_command=prim_asrt__constant(
                asrt_command.matches_executable_file_command_driver(
                    asrt_path.path_as_str(asrt.equals(sys.executable)),
                )),
        ),
        Case(
            'system program',
            command_renderer=pgm_args.system_program_command_line(system_program),
            expected_command=prim_asrt__constant(
                asrt_command.matches_system_program_command_driver(
                    asrt.equals(system_program)
                ))
        ),
        Case(
            'reference',
            command_renderer=pgm_args.symbol_ref_command_line(program_symbol.name),
            symbols=[program_symbol],
            expected_command=prim_asrt__constant(
                asrt_command.matches_system_program_command_driver(
                    asrt.equals(system_program)
                )),
        ),
    ]


def _single_line_command_cases__wo_argument_list() -> List[Case]:
    shell_command_line = 'the shell command line'

    return [
        Case(
            'shell',
            command_renderer=pgm_args.shell_command_line(shell_command_line),
            expected_command=prim_asrt__constant(
                asrt_command.matches_shell_command_driver(asrt.equals(shell_command_line))
            )
        ),
    ]


def _single_line_command_cases() -> List[Case]:
    return _single_line_command_cases__w_argument_list() + _single_line_command_cases__wo_argument_list()


CHECKER_WO_EXECUTION = IntegrationChecker(
    parse_program.program_parser(),
    integration_check_config.ProgramPropertiesConfiguration(
        integration_check_applier.NullApplier(),
    ),
    True,
)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
