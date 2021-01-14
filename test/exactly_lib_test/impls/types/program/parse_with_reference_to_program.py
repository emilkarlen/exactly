import unittest
from typing import List, Sequence, Callable

from exactly_lib.impls.types.program.command import driver_sdvs
from exactly_lib.impls.types.program.parse import parse_with_reference_to_program as sut
from exactly_lib.impls.types.program.sdvs import command_program_sdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.list_ import list_sdvs
from exactly_lib.type_val_deps.types.path import path_sdvs, path_ddvs
from exactly_lib.type_val_deps.types.path.path_ddvs import simple_of_rel_option
from exactly_lib.type_val_deps.types.path.path_sdvs import constant
from exactly_lib.type_val_deps.types.program.sdv.accumulated_components import AccumulatedComponents
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_deps.types.program.sdv.command import CommandDriverSdv, CommandSdv
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.type_val_prims.program.command import CommandDriver
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import QuoteType, QUOTE_CHAR_FOR_TYPE
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.logic.test_resources import integration_check
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_wo_tcds, MultiSourceExpectation, \
    AssertionResolvingEnvironment, arrangement_w_tcds, ExecutionExpectation, Expectation, ParseExpectation, Arrangement
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc
from exactly_lib_test.impls.types.program.test_resources import integration_check_applier
from exactly_lib_test.impls.types.program.test_resources import integration_check_config
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.test_resources import relativity_options
from exactly_lib_test.impls.types.test_resources.validation_of_path import FAILING_VALIDATION_ASSERTION_FOR_PARTITION
from exactly_lib_test.section_document.element_parsers.test_resources.parsing import ParserAsLocationAwareParser
from exactly_lib_test.section_document.test_resources import parse_checker
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.data.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes__raw import \
    RawProgramOfSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stx import ArgumentOfStringAbsStx, \
    ArgumentOfSymbolReferenceAbsStx, ArgumentOfExistingPathAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources import program as asrt_pgm
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command, \
    program_assertions as asrt_pgm_val
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes_str, surrounded_by_soft_quotes_str


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestFailingParse(),
        TestResolvingAndSymbolReferences(),
        unittest.makeSuite(TestValidation),
        TestResolvingAndAccumulation(),
    ])


class TestFailingParse(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NameAndValue('empty source',
                         RawProgramOfSymbolReferenceAbsStx('')
                         ),
            NameAndValue('not a plain symbol name - quoted - hard',
                         RawProgramOfSymbolReferenceAbsStx(surrounded_by_hard_quotes_str('valid_symbol_name'))
                         ),
            NameAndValue('not a plain symbol name - quoted - soft',
                         RawProgramOfSymbolReferenceAbsStx(surrounded_by_soft_quotes_str('valid_symbol_name'))
                         ),
            NameAndValue('not a plain symbol name - symbol reference',
                         RawProgramOfSymbolReferenceAbsStx(symbol_reference_syntax_for_name('valid_symbol_name'))
                         ),
            NameAndValue('not a plain symbol name - broken syntax due to missing end quote',
                         RawProgramOfSymbolReferenceAbsStx(QUOTE_CHAR_FOR_TYPE[QuoteType.SOFT] + 'valid_symbol_name')
                         ),
            NameAndValue('valid symbol name - broken argument syntax due to missing end quote',
                         RawProgramOfSymbolReferenceAbsStx(
                             'valid_symbol_name',
                             [ArgumentOfStringAbsStx.of_str(QUOTE_CHAR_FOR_TYPE[QuoteType.SOFT] + 'argument')],
                         )
                         ),
        ]
        checker = parse_checker.Checker(ParserAsLocationAwareParser(sut.program_parser()))
        for case in cases:
            checker.check_invalid_syntax__abs_stx(self, case.value)


class SymbolReferencesCase:
    def __init__(self,
                 name: str,
                 source: AbstractSyntax,
                 references_expectation: ValueAssertion[Sequence[SymbolReference]],
                 expected_additional_arguments: List[str],
                 ):
        self.name = name
        self.source = source
        self.references_expectation = references_expectation
        self.expected_additional_arguments = expected_additional_arguments


class TestResolvingAndSymbolReferences(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        referenced_system_program_name = 'the-referenced-system-program'
        referenced_program_arguments = ['arg 1 of referenced', 'arg 2 of referenced']
        referenced_system_program_sdv = program_sdvs.system_program(
            string_sdvs.str_constant(referenced_system_program_name),
            ArgumentsSdv.new_without_validation(
                list_sdvs.from_str_constants(referenced_program_arguments)
            )
        )

        program_symbol = ProgramSymbolContext.of_sdv('PROGRAM_SYMBOL', referenced_system_program_sdv)
        argument_symbol = StringConstantSymbolContext('ARGUMENT_SYMBOL', 'string argument')
        symbols = SymbolContext.symbol_table_of_contexts([program_symbol, argument_symbol])

        cases = [
            SymbolReferencesCase(
                'just program reference symbol',
                RawProgramOfSymbolReferenceAbsStx(program_symbol.name),
                references_expectation=
                asrt.matches_sequence([
                    asrt_pgm.is_reference_to_program(program_symbol.name),
                ]),
                expected_additional_arguments=[],
            ),
            SymbolReferencesCase(
                'single argument that is a reference to a symbol',
                RawProgramOfSymbolReferenceAbsStx(
                    program_symbol.name,
                    [ArgumentOfSymbolReferenceAbsStx(argument_symbol.name)]
                ),
                references_expectation=
                asrt.matches_sequence([
                    asrt_pgm.is_reference_to_program(program_symbol.name),
                    asrt_sym_ref.is_reference_to_data_type_symbol(argument_symbol.name),
                ]),
                expected_additional_arguments=[argument_symbol.str_value],
            ),
        ]
        for case in cases:
            def expected_program(env: AssertionResolvingEnvironment) -> ValueAssertion[Program]:
                return asrt_pgm_val.matches_program(
                    command=asrt_command.equals_system_program_command(
                        program=referenced_system_program_name,
                        arguments=referenced_program_arguments + case.expected_additional_arguments,
                    ),
                    stdin=asrt_pgm_val.is_no_stdin(),
                    transformer=asrt_pgm_val.is_no_transformation(),
                )

            expectation = MultiSourceExpectation(
                symbol_references=case.references_expectation,
                primitive=expected_program,
            )

            with self.subTest(case=case.name):
                # ACT & ASSERT #
                CHECKER_WO_EXECUTION.check__abs_stx__std_layouts__mk_source_variants__wo_input(
                    self,
                    equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
                    case.source,
                    arrangement_wo_tcds(
                        symbols=symbols,
                    ),
                    expectation,
                )


class TestValidation(unittest.TestCase):
    def test_failing_validation_of_referenced_program__pre_sds(self):
        self._check_failing_validation_of_referenced_program__for_relativity(RelOptionType.REL_HDS_ACT)

    def test_failing_validation_of_referenced_program__post_sds(self):
        self._check_failing_validation_of_referenced_program__for_relativity(RelOptionType.REL_TMP)

    def test_failing_validation_of_accumulated_argument__pre_sds(self):
        self._check_failing_validation_of_accumulated_argument__for_relativity(RelOptionType.REL_HDS_CASE)

    def test_failing_validation_of_accumulated_argument__post_sds(self):
        self._check_failing_validation_of_accumulated_argument__for_relativity(RelOptionType.REL_ACT)

    def _check_failing_validation_of_referenced_program__for_relativity(self, missing_file_relativity: RelOptionType):
        relativity_conf = relativity_options.conf_rel_any(missing_file_relativity)

        program_symbol_with_ref_to_non_exiting_exe_file = ProgramSymbolContext.of_sdv(
            'PGM_WITH_REF_TO_EXE_FILE',
            program_sdvs.ref_to_exe_file(
                constant(simple_of_rel_option(relativity_conf.relativity_option,
                                              'non-existing-exe-file')))
        )

        program_symbol_with_ref_to_non_exiting_file_as_argument = ProgramSymbolContext.of_sdv(
            'PGM_WITH_ARG_WITH_REF_TO_FILE',
            program_sdvs.interpret_py_source_file_that_must_exist(
                constant(simple_of_rel_option(relativity_conf.relativity_option,
                                              'non-existing-python-file.py')))
        )

        expectation = MultiSourceExpectation.of_const(
            symbol_references=asrt.anything_goes(),
            primitive=asrt.anything_goes(),
            execution=ExecutionExpectation(
                validation=FAILING_VALIDATION_ASSERTION_FOR_PARTITION[relativity_conf.directory_structure_partition],
            )
        )

        symbols = SymbolContext.symbol_table_of_contexts([
            program_symbol_with_ref_to_non_exiting_exe_file,
            program_symbol_with_ref_to_non_exiting_file_as_argument,
        ])
        arrangement = arrangement_w_tcds(
            symbols=symbols,
        )

        cases = [
            NameAndValue(
                'executable does not exist',
                RawProgramOfSymbolReferenceAbsStx(program_symbol_with_ref_to_non_exiting_exe_file.name),
            ),
            NameAndValue(
                'file referenced from argument does not exist',
                RawProgramOfSymbolReferenceAbsStx(program_symbol_with_ref_to_non_exiting_file_as_argument.name),
            ),
        ]

        for case in cases:
            with self.subTest(case=case.name):
                # ACT & ASSERT #
                CHECKER_WO_EXECUTION.check__abs_stx__std_layouts__mk_source_variants__wo_input(
                    self,
                    equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
                    case.value,
                    arrangement,
                    expectation,
                )

    def _check_failing_validation_of_accumulated_argument__for_relativity(self, missing_file_relativity: RelOptionType):
        relativity_conf = relativity_options.conf_rel_any(missing_file_relativity)

        referenced_program_arguments = ['valid arg 1 of referenced', 'valid arg 2 of referenced']
        referenced_system_program_sdv = program_sdvs.system_program(
            string_sdvs.str_constant('valid-system-program'),
            ArgumentsSdv.new_without_validation(
                list_sdvs.from_str_constants(referenced_program_arguments)
            )
        )

        valid_program_symbol = ProgramSymbolContext.of_sdv(
            'VALID_PROGRAM',
            referenced_system_program_sdv
        )

        invalid_argument_syntax = ArgumentOfExistingPathAbsStx(
            relativity_conf.path_abs_stx_of_name('non-existing-file')
        )
        referenced_valid_program_syntax = RawProgramOfSymbolReferenceAbsStx(valid_program_symbol.name)
        reference_and_additional_invalid_argument = referenced_valid_program_syntax.new_w_additional_arguments(
            [invalid_argument_syntax]
        )
        # ACT & ASSERT #
        CHECKER_WO_EXECUTION.check__abs_stx__std_layouts__mk_source_variants__wo_input(
            self,
            equivalent_source_variants__for_consume_until_end_of_last_line__s__nsc,
            reference_and_additional_invalid_argument,
            arrangement_w_tcds(
                symbols=valid_program_symbol.symbol_table,
            ),
            MultiSourceExpectation.of_const(
                symbol_references=valid_program_symbol.references_assertion,
                primitive=asrt.anything_goes(),
                execution=ExecutionExpectation(
                    validation=
                    FAILING_VALIDATION_ASSERTION_FOR_PARTITION[relativity_conf.directory_structure_partition],
                )
            ),
        )


class CommandDriverCase:
    def __init__(self,
                 name: str,
                 command_driver: CommandDriverSdv,
                 expected_command_driver: Callable[[AssertionResolvingEnvironment], ValueAssertion[CommandDriver]],
                 mk_arrangement: Callable[[SymbolTable], Arrangement],
                 ):
        self.name = name
        self.command_driver = command_driver
        self.expected_command_driver = expected_command_driver
        self.mk_arrangement = mk_arrangement


class TestResolvingAndAccumulation(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        system_program_name = 'system-program'
        executable_program_file_name = 'executable-program-file'
        executable_file_relativity = relativity_options.conf_rel_any(RelOptionType.REL_HDS_ACT)
        executable_file_ddv = path_ddvs.of_rel_option(
            executable_file_relativity.relativity_option,
            path_ddvs.constant_path_part(executable_program_file_name)
        )
        shell_initial_command = 'shell initial command'

        def mk_arrangement__executable_file(symbols: SymbolTable) -> Arrangement:
            return arrangement_w_tcds(
                symbols=symbols,
                tcds_contents=executable_file_relativity.populator_for_relativity_option_root(
                    fs.DirContents([fs.executable_file(executable_program_file_name)])
                )
            )

        def expected_command_driver__system_program(env: AssertionResolvingEnvironment
                                                    ) -> ValueAssertion[CommandDriver]:
            return asrt_command.matches_system_program_command_driver(
                asrt.equals(system_program_name)
            )

        def expected_command_driver__executable_file(env: AssertionResolvingEnvironment
                                                     ) -> ValueAssertion[CommandDriver]:
            return asrt_command.matches_executable_file_command_driver(
                asrt.equals(executable_file_ddv.value_of_any_dependency__d(env.tcds).primitive),
            )

        def expected_command_driver__shell_cmd_line(env: AssertionResolvingEnvironment
                                                    ) -> ValueAssertion[CommandDriver]:
            return asrt_command.matches_shell_command_driver(
                asrt.equals(shell_initial_command)
            )

        command_driver_sdv_cases = [
            CommandDriverCase(
                'system program',
                command_driver=driver_sdvs.CommandDriverSdvForSystemProgram(
                    string_sdvs.str_constant(system_program_name)
                ),
                expected_command_driver=expected_command_driver__system_program,
                mk_arrangement=lambda sym_tbl: arrangement_wo_tcds(symbols=sym_tbl),
            ),
            CommandDriverCase(
                'executable program file',
                command_driver=driver_sdvs.CommandDriverSdvForExecutableFile(
                    path_sdvs.constant(executable_file_ddv)
                ),
                expected_command_driver=expected_command_driver__executable_file,
                mk_arrangement=mk_arrangement__executable_file,
            ),
            CommandDriverCase(
                'shell command line',
                command_driver=driver_sdvs.CommandDriverSdvForShell(
                    string_sdvs.str_constant(shell_initial_command)
                ),
                expected_command_driver=expected_command_driver__shell_cmd_line,
                mk_arrangement=lambda sym_tbl: arrangement_wo_tcds(symbols=sym_tbl),
            ),
        ]

        arguments_cases = [
            NameAndValue(
                '{} arguments'.format(n),
                ['arg{}'.format(i + 1) for i in range(n)],
            )
            for n in [0, 1, 2]
        ]

        for command_driver_case in command_driver_sdv_cases:
            for arguments_of_referenced_command_case in arguments_cases:
                for accumulated_arguments_of_referenced_program_case in arguments_cases:
                    for additional_arguments_case in arguments_cases:
                        with self.subTest(
                                driver=command_driver_case.name,
                                args_of_referenced_command=arguments_of_referenced_command_case.name,
                                accumulated_args_of_referenced_program=accumulated_arguments_of_referenced_program_case.name,
                                additional_args=additional_arguments_case.name,
                        ):
                            # ACT & ASSERT #
                            self._check(command_driver_case,
                                        arguments_of_referenced_command_case.value,
                                        accumulated_arguments_of_referenced_program_case.value,
                                        additional_arguments_case.value)

    def _check(self,
               command_driver: CommandDriverCase,
               arguments_of_referenced_command: List[str],
               accumulated_arguments_of_referenced_program: List[str],
               additional_argument: List[str],
               ):
        # ARRANGE #
        all_arguments = (
                arguments_of_referenced_command +
                accumulated_arguments_of_referenced_program +
                additional_argument
        )

        def expected_program(env: AssertionResolvingEnvironment) -> ValueAssertion[Program]:
            return asrt_pgm_val.matches_program(
                asrt_command.matches_command(
                    driver=command_driver.expected_command_driver(env),
                    arguments=asrt.equals(all_arguments)
                ),
                stdin=asrt_pgm_val.is_no_stdin(),
                transformer=asrt_pgm_val.is_no_transformation(),
            )

        referenced_program_symbol = ProgramSymbolContext.of_sdv(
            'REFERENCED_PROGRAM',
            command_program_sdv.ProgramSdvForCommand(
                CommandSdv(
                    command_driver.command_driver,
                    ArgumentsSdv.new_without_validation(
                        list_sdvs.from_str_constants(arguments_of_referenced_command)
                    )
                ),
                AccumulatedComponents.of_arguments(
                    ArgumentsSdv.new_without_validation(
                        list_sdvs.from_str_constants(accumulated_arguments_of_referenced_program)
                    )
                )
            )
        )
        syntax = RawProgramOfSymbolReferenceAbsStx(
            referenced_program_symbol.name,
            [
                ArgumentOfStringAbsStx.of_str(arg)
                for arg in additional_argument
            ],
        )
        # ACT & ASSERT #
        CHECKER_WO_EXECUTION.check__abs_stx__wo_input(
            self,
            syntax,
            command_driver.mk_arrangement(referenced_program_symbol.symbol_table),
            Expectation(
                parse=ParseExpectation(
                    symbol_references=referenced_program_symbol.references_assertion,
                ),
                primitive=expected_program,
            ),
        )


CHECKER_WO_EXECUTION = integration_check.IntegrationChecker(
    sut.program_parser(),
    integration_check_config.ProgramPropertiesConfiguration(
        integration_check_applier.NullApplier(),
    ),
    True,
)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
