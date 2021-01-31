import unittest
from typing import Sequence

from exactly_lib.impls.instructions.multi_phase import sys_cmd as sut
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.parse.token import HARD_QUOTE_CHAR
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.impls.actors.program.test_resources import tmp_dir_in_path_with_files
from exactly_lib_test.impls.instructions.configuration.actor.test_resources import ExecutedCommandAssertion
from exactly_lib_test.impls.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.impls.instructions.multi_phase.test_resources.sys_cmd import command_line
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.impls.types.program.test_resources import result_assertions, program_arguments
from exactly_lib_test.impls.types.test_resources import arguments_building as ab
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources import path_arguments
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatRecordsArguments, \
    CommandExecutorThatRaisesHardError, CommandExecutorThatJustReturnsConstant
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.data.test_resources import concrete_restriction_assertion as asrt_rest
from exactly_lib_test.type_val_deps.types.list_.test_resources.list_ import ListConstantSymbolContext
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command
from exactly_lib_test.util.process_execution.test_resources.proc_exe_env import proc_exe_env_for_test


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSystemProgramIsExecuted(),
        TestSymbolReferences(),
        TestArgumentsShouldBeValidated(),
        TestHardErrorFromExecution(),
        TestNonZeroExitCodeFromExecution(),
        TestContentsOfStdinShouldBeEmpty(),
        unittest.makeSuite(TestFailingParse),
        suite_for_instruction_documentation(sut.DescriptionForNonAssertPhaseInstruction('instruction name',
                                                                                        'section_name'))
    ])


CHECKER = embryo_check.Checker(sut.embryo_parser('instruction-name'))


class ArgumentsCase:
    def __init__(self,
                 name: str,
                 arguments: ArgumentElementsRenderer,
                 expected_arguments: Assertion[Sequence[str]],
                 symbols: Sequence[SymbolContext] = (),
                 ):
        self.name = name
        self.arguments = arguments
        self.symbols = symbols
        self.expected_arguments = expected_arguments


class TestSystemProgramIsExecuted(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        argument_1 = 'argument-1'
        argument_2 = 'argument-2'
        illegally_quoted = 'abc{} cde'.format(HARD_QUOTE_CHAR)
        list_symbol = ListConstantSymbolContext(
            'list_symbol',
            ['1st', '2nd with space'],
        )
        cases = [
            ArgumentsCase(
                'no arguments',
                ab.empty(),
                asrt.is_empty_sequence,
            ),
            ArgumentsCase(
                'simple arguments',
                ab.sequence__r([
                    program_arguments.simple(argument_1),
                    program_arguments.simple(argument_2),
                ]),
                asrt.equals([argument_1, argument_2]),
            ),
            ArgumentsCase(
                'list symbol reference',
                program_arguments.simple(list_symbol.name__sym_ref_syntax),
                asrt.equals(list_symbol.constant_list),
                [list_symbol],
            ),
            ArgumentsCase(
                'special PROGRAM-ARGUMENT',
                program_arguments.remaining_part_of_current_line_as_literal(illegally_quoted),
                asrt.equals([illegally_quoted]),
            ),
        ]

        program_name = 'program'
        for case in cases:
            expected_command = asrt_command.matches_command(
                driver=asrt_command.matches_system_program_command_driver(
                    asrt.equals(program_name)
                ),
                arguments=case.expected_arguments
            )

            with self.subTest(case.name):
                # ACT & ASSERT #
                check_successful_execution(
                    self,
                    arguments=command_line(
                        program_name,
                        case.arguments,
                    ),
                    expected_command=expected_command,
                    symbols=SymbolContext.symbol_table_of_contexts(case.symbols),
                    symbol_usages=SymbolContext.usages_assertion_of_contexts(case.symbols)
                )


class TestSymbolReferences(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        program_symbol = StringConstantSymbolContext(
            'program_name_symbol',
            'the-program',
            default_restrictions=asrt_rest.is_string_made_up_of_just_strings_reference_restrictions(),
        )
        argument_list_symbol = ListConstantSymbolContext(
            'arguments_symbol',
            ['1st', '2nd'],
        )
        symbols = [program_symbol, argument_list_symbol]

        expected_command = asrt_command.matches_command(
            driver=asrt_command.matches_system_program_command_driver(
                asrt.equals(program_symbol.str_value)
            ),
            arguments=asrt.equals(argument_list_symbol.constant),
        )

        # ACT & ASSERT #
        check_successful_execution(
            self,
            arguments=command_line(
                program_symbol.name__sym_ref_syntax,
                program_arguments.simple(argument_list_symbol.name__sym_ref_syntax),
            ),
            expected_command=expected_command,
            symbols=SymbolContext.symbol_table_of_contexts(symbols),
            symbol_usages=SymbolContext.usages_assertion_of_contexts(symbols)
        )


class TestArgumentsShouldBeValidated(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'pre sds',
                (
                    RelOptionType.REL_HDS_CASE,
                    ValidationAssertions.pre_sds_fails__w_any_msg(),
                ),
            ),
            NameAndValue(
                'post sds',
                (
                    RelOptionType.REL_ACT,
                    ValidationAssertions.post_sds_fails__w_any_msg(),
                ),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                CHECKER.check__w_source_variants(
                    self,
                    command_line(
                        'program',
                        program_arguments.existing_path(
                            path_arguments.RelOptPathArgument('name', case.value[0]),
                        )
                    ).as_str,
                    ArrangementWithSds(),
                    embryo_check.MultiSourceExpectation(
                        validation=case.value[1],
                    ),
                )


class TestHardErrorFromExecution(unittest.TestCase):
    def runTest(self):
        CHECKER.check__w_source_variants(
            self,
            command_line(
                'program',
            ).as_str,
            ArrangementWithSds(
                os_services=os_services_access.new_for_cmd_exe(
                    CommandExecutorThatRaisesHardError(
                        asrt_text_doc.new_single_string_text_for_test('the error message')
                    )
                ),
            ),
            embryo_check.MultiSourceExpectation(
                main_raises_hard_error=True
            ),
        )


class TestNonZeroExitCodeFromExecution(unittest.TestCase):
    def runTest(self):
        executor = CommandExecutorThatJustReturnsConstant(
            1,
            string_to_write_to_stderr='output on stderr'
        )
        CHECKER.check__w_source_variants(
            self,
            command_line(
                'program',
            ).as_str,
            ArrangementWithSds(
                os_services=os_services_access.new_for_cmd_exe(executor),
            ),
            embryo_check.MultiSourceExpectation(
                main_result=result_assertions.equals(executor.constant_return_value,
                                                     executor.string_to_write_to_stderr),
            ),
        )


class TestContentsOfStdinShouldBeEmpty(unittest.TestCase):
    def runTest(self):
        non_zero_exit_code = 1
        exe_file = fs.python_executable_file(
            'program-name',
            py_programs.copy_stdin_to_stderr_and_exit_with(non_zero_exit_code)
        )
        with tmp_dir_in_path_with_files(fs.DirContents([exe_file])) as env:
            # ACT & ASSERT #
            CHECKER.check(
                self,
                command_line(
                    exe_file.name,
                ).as_remaining_source,
                ArrangementWithSds(
                    process_execution_settings=proc_exe_env_for_test(environ=env)
                ),
                embryo_check.expectation(
                    source=asrt_source.source_is_at_end,
                    main_result=result_assertions.equals(non_zero_exit_code, ''),
                ),
            )


class TestFailingParse(unittest.TestCase):
    def test_fail_when_only_white_space_on_line(self):
        # ARRANGE #
        parser = sut.embryo_parser('instruction-name')
        for source in equivalent_source_variants(self, '   '):
            # ACT & ASSERT #
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                parser.parse(ARBITRARY_FS_LOCATION_INFO, source)

    def test_fail_when_program_name_has_invalid_quoting(self):
        # ARRANGE #
        invalid_program_name = HARD_QUOTE_CHAR
        parser = sut.embryo_parser('instruction-name')
        # ACT & ASSERT #
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.parse(ARBITRARY_FS_LOCATION_INFO,
                         remaining_source(invalid_program_name))

    def test_fail_when_argument_has_invalid_quoting(self):
        # ARRANGE #
        program_and_arguments = 'program-name arg {}un-ended'.format(HARD_QUOTE_CHAR)
        parser = sut.embryo_parser('instruction-name')
        # ACT & ASSERT #
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.parse(ARBITRARY_FS_LOCATION_INFO,
                         remaining_source(program_and_arguments))


def check_successful_execution(put: unittest.TestCase,
                               arguments: ArgumentElementsRenderer,
                               symbols: SymbolTable,
                               symbol_usages: Assertion[Sequence[SymbolUsage]],
                               expected_command: Assertion[Command],
                               ):
    executor_that_records_arguments = CommandExecutorThatRecordsArguments()
    CHECKER.check__w_source_variants(
        put,
        arguments.as_str,
        ArrangementWithSds(
            os_services=os_services_access.new_for_cmd_exe(executor_that_records_arguments),
            symbols=symbols,
        ),
        embryo_check.MultiSourceExpectation(
            symbol_usages=symbol_usages,
            side_effects_on_tcds=ExecutedCommandAssertion(
                executor_that_records_arguments,
                lambda tcds: expected_command,
            ),
            main_result=result_assertions.equals(0, None),
        ),
    )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
