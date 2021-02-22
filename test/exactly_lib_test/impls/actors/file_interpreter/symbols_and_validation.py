import pathlib
import sys
import unittest

from exactly_lib.impls.actors import file_interpreter as sut
from exactly_lib.impls.os_services import os_services_access
from exactly_lib.impls.types.program.command import command_sdvs, arguments_sdvs
from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.types.path import path_ddvs, path_sdvs
from exactly_lib.type_val_deps.types.program.sdv.arguments import ArgumentsSdv
from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.util.parse.token import SOFT_QUOTE_CHAR
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.impls.actors.file_interpreter.configuration import COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE
from exactly_lib_test.impls.actors.test_resources import integration_check
from exactly_lib_test.impls.actors.test_resources import relativity_configurations
from exactly_lib_test.impls.actors.test_resources.integration_check import Arrangement, arrangement_w_tcds
from exactly_lib_test.impls.actors.test_resources.integration_check import Expectation, \
    check_execution, PostSdsExpectation
from exactly_lib_test.impls.actors.test_resources.misc import PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN
from exactly_lib_test.impls.actors.test_resources.validation_cases import VALIDATION_CASES
from exactly_lib_test.impls.instructions.configuration.actor.test_resources import ExecutedCommandAssertion
from exactly_lib_test.impls.test_resources.validation.svh_validation import ValidationExpectationSvh
from exactly_lib_test.impls.types.program.test_resources import program_arguments
from exactly_lib_test.impls.types.test_resources import arguments_building as ab, relativity_options
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources import hds_populators, path_arguments
from exactly_lib_test.tcfs.test_resources.hds_populators import contents_in
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatRecordsArguments
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import Dir
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_pr
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.list_.test_resources.list_ import ListConstantSymbolContext
from exactly_lib_test.type_val_deps.types.path.test_resources.path import ConstantSuffixPathDdvSymbolContext, \
    PathSymbolContext
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command
from exactly_lib_test.util.test_resources.py_program import \
    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()

    ret_val.addTest(TestValidationShouldFailWhenInterpreterProgramFileDoesNotExist())
    ret_val.addTest(TestValidationShouldFailWhenInterpreterProgramFileIsADirectory())

    ret_val.addTest(TestValidationShouldFailWhenSourceFileDoesNotExist())
    ret_val.addTest(TestValidationShouldFailWhenSourceFileIsADirectory())

    ret_val.addTest(TestArgumentsAreProgramArguments())
    ret_val.addTest(TestArgumentsOfInterpreterAndActAreConcatenated())
    ret_val.addTest(unittest.makeSuite(TestValidationOfArguments))

    ret_val.addTest(TestStringSymbolReferenceInInterpreter())
    ret_val.addTest(TestStringSymbolReferenceInSourceAndArgument())
    ret_val.addTest(TestMultipleSymbolReferencesInSourceFileRef())

    return ret_val


class TestCaseWInterpreterThatRunsPythonProgramFileBase(unittest.TestCase):
    def _check(self,
               command_line: str,
               arrangement: Arrangement,
               expectation: Expectation):
        check_execution(self,
                        sut.actor(COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE),
                        [instr([command_line])],
                        arrangement,
                        expectation)


class TestValidationShouldFailWhenSourceFileDoesNotExist(TestCaseWInterpreterThatRunsPythonProgramFileBase):
    def runTest(self):
        command_line = 'non-existing-file.src'
        arrangement = arrangement_w_tcds()

        expectation = Expectation(
            validation=ValidationExpectationSvh.fails__pre_sds()
        )
        self._check(command_line,
                    arrangement,
                    expectation)


class TestValidationShouldFailWhenSourceFileIsADirectory(TestCaseWInterpreterThatRunsPythonProgramFileBase):
    def runTest(self):
        source_file = 'source-file.src'
        command_line = source_file
        arrangement = arrangement_w_tcds(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, fs.DirContents([
                Dir.empty(source_file)]))
        )
        expectation = Expectation(
            validation=ValidationExpectationSvh.fails__pre_sds()
        )
        self._check(command_line,
                    arrangement,
                    expectation)


class TestStringSymbolReferenceInSourceAndArgument(TestCaseWInterpreterThatRunsPythonProgramFileBase):
    def runTest(self):
        symbol_for_source_file = StringConstantSymbolContext('source_file_symbol_name',
                                                             'the-source-file.py')

        argument_symbol = StringConstantSymbolContext('argument_symbol_name', 'string-constant')

        expected_output = lines_content([argument_symbol.str_value])

        command_line = '{source_file} {argument} '.format(
            source_file=symbol_for_source_file.name__sym_ref_syntax,
            argument=argument_symbol.name__sym_ref_syntax,
        )

        arrangement = arrangement_w_tcds(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, fs.DirContents([
                fs.File(
                    symbol_for_source_file.str_value,
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ])),
            symbol_table=SymbolContext.symbol_table_of_contexts([
                symbol_for_source_file,
                argument_symbol,
            ])
        )

        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                symbol_for_source_file.reference_assertion__path_or_string(PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN),
                argument_symbol.reference_assertion__convertible_to_string,
            ]),
            execute=eh_assertions.is_exit_code(0),
            post_sds=PostSdsExpectation.constant(
                sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                      'CLI arguments, one per line'))
            ),
        )
        self._check(command_line,
                    arrangement,
                    expectation)


class TestMultipleSymbolReferencesInSourceFileRef(TestCaseWInterpreterThatRunsPythonProgramFileBase):
    def runTest(self):
        sub_dir_of_home = 'sub-dir'
        dir_symbol = ConstantSuffixPathDdvSymbolContext('dir_symbol_name',
                                                        RelOptionType.REL_HDS_ACT,
                                                        sub_dir_of_home,
                                                        PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN)

        source_file_name_symbol = StringConstantSymbolContext('source_file_name_symbol_name',
                                                              'the-source-file.py')

        argument = 'argument_string'

        expected_output = lines_content([argument])

        command_line = '{dir}/{file_name}  {argument} '.format(
            dir=dir_symbol.name__sym_ref_syntax,
            file_name=source_file_name_symbol.name__sym_ref_syntax,
            argument=argument,
        )

        executable_file = fs.File(
            source_file_name_symbol.str_value,
            PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)

        arrangement = arrangement_w_tcds(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, fs.DirContents([
                fs.Dir(sub_dir_of_home, [executable_file])
            ])),
            symbol_table=SymbolContext.symbol_table_of_contexts([
                dir_symbol,
                source_file_name_symbol,
            ])
        )

        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                dir_symbol.reference_assertion__path_or_string,
                source_file_name_symbol.reference_assertion__path_component,
            ]),
            execute=eh_assertions.is_exit_code(0),
            post_sds=PostSdsExpectation.constant(
                sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                      'CLI arguments, one per line'))
            ),
        )
        self._check(command_line,
                    arrangement,
                    expectation)


class TestStringSymbolReferenceInInterpreter(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        source_file = fs.File.empty('source-file.src')

        python_interpreter_symbol = PathSymbolContext.of_sdv(
            'PYTHON_INTERPRETER_SYMBOL',
            path_sdvs.constant(
                path_ddvs.absolute_path(pathlib.Path(sys.executable))
            ),
        )

        interpreter_with_symbol_reference = command_sdvs.for_executable_file(
            python_interpreter_symbol.reference_sdv__path_or_string(
                relativity_configurations.INTERPRETER_FILE.relativity
            )
        )

        arrangement = arrangement_w_tcds(
            symbol_table=python_interpreter_symbol.symbol_table,
            hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                fs.DirContents([source_file])
            )
        )
        expectation = Expectation(
            symbol_usages=asrt.matches_singleton_sequence(
                python_interpreter_symbol.reference_assertion__path_or_string),
            post_sds=PostSdsExpectation.constant(
                sub_process_result_from_execute=asrt_pr.sub_process_result(
                    exitcode=asrt.equals(0),
                    stdout=asrt.equals(''),
                    stderr=asrt.equals(''),
                )
            ),
        )
        # ACT & ASSERT #
        check_execution(self,
                        sut.actor(interpreter_with_symbol_reference),
                        [instr([source_file.name])],
                        arrangement,
                        expectation,
                        )


class TestValidationShouldFailWhenInterpreterProgramFileDoesNotExist(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        source_file = fs.File.empty('source-file.src')

        interpreter_with_non_existing_program_file = command_sdvs.for_executable_file(
            path_sdvs.constant(
                path_ddvs.rel_hds(relativity_configurations.INTERPRETER_FILE.relativity_option_rel_hds,
                                  path_ddvs.constant_path_part('non-existing'))),
        )

        arrangement = arrangement_w_tcds(
            hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                fs.DirContents([source_file])
            )
        )

        expectation = Expectation(
            validation=ValidationExpectationSvh.fails__pre_sds()
        )
        # ACT & ASSERT #
        check_execution(self,
                        sut.actor(interpreter_with_non_existing_program_file),
                        [instr([source_file.name])],
                        arrangement,
                        expectation)


class TestValidationShouldFailWhenInterpreterProgramFileIsADirectory(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        source_file = fs.File.empty('source-file.src')
        a_dir = fs.Dir.empty('a-dir')

        interpreter_with_program_that_is_a_dir = command_sdvs.for_executable_file(
            path_sdvs.constant(
                path_ddvs.rel_hds(relativity_configurations.INTERPRETER_FILE.relativity_option_rel_hds,
                                  path_ddvs.constant_path_part(a_dir.name))),
        )

        command_line = source_file
        arrangement = arrangement_w_tcds(
            hds_contents=hds_populators.multiple([
                relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                    fs.DirContents([source_file])
                ),
                relativity_configurations.INTERPRETER_FILE.populator_for_relativity_option_root__hds(
                    fs.DirContents([a_dir])
                ),
            ])
        )
        expectation = Expectation(
            validation=ValidationExpectationSvh.fails__pre_sds()
        )
        # ACT & ASSERT #
        check_execution(self,
                        sut.actor(interpreter_with_program_that_is_a_dir),
                        [instr([command_line.name])],
                        arrangement,
                        expectation)


class TestValidationOfArguments(unittest.TestCase):
    def test_arguments_of_interpreter(self):
        # ARRANGE #
        exe_file = fs.python_executable_file(
            'program-name',
            py_programs.exit_with(0)
        )
        for case in VALIDATION_CASES:
            with self.subTest(case.name):
                interpreter_arguments = arguments_sdvs.ref_to_path_that_must_exist(
                    path_sdvs.of_rel_option_with_const_file_name(case.path_relativity,
                                                                 'non-existing-file')
                )
                actor = sut.actor(
                    command_sdvs.for_executable_file(
                        path_sdvs.constant(path_ddvs.absolute_file_name(sys.executable)),
                        interpreter_arguments
                    )
                )
                act_instruction = instr([exe_file.name])
                # ACT & ASSERT #
                integration_check.check_execution(
                    self,
                    actor,
                    [act_instruction],
                    arrangement_w_tcds(
                        hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                            fs.DirContents([exe_file])
                        )
                    ),
                    Expectation(validation=case.expectation),
                )

    def test_arguments_of_program_file(self):
        # ARRANGE #
        exe_file = fs.python_executable_file(
            'program-name',
            py_programs.exit_with(0)
        )
        actor = sut.actor(COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE)
        for case in VALIDATION_CASES:
            with self.subTest(case.name):
                act_contents = ab.sequence__r([
                    ab.singleton(exe_file.name),
                    program_arguments.existing_file(
                        path_arguments.RelOptPathArgument('non-existing',
                                                          case.path_relativity)
                    )
                ])
                act_instruction = instr([act_contents.as_str])
                # ACT & ASSERT #
                integration_check.check_execution(
                    self,
                    actor,
                    [act_instruction],
                    arrangement_w_tcds(
                        hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                            fs.DirContents([exe_file])
                        )
                    ),
                    Expectation(validation=case.expectation),
                )


class TestArgumentsAreProgramArguments(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        actor = sut.actor(COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE)

        exe_file = fs.python_executable_file(
            'program-name',
            py_programs.exit_with_0()
        )
        text_until_end_of_line = 'some {}invalidly quoted text'.format(SOFT_QUOTE_CHAR)

        existing_path_relativity = relativity_options.conf_rel_hds(RelHdsOptionType.REL_HDS_CASE)

        existing_path_argument = path_arguments.RelOptPathArgument(
            'existing-path',
            existing_path_relativity.relativity,
        )
        act_contents = ab.sequence__r([
            ab.singleton(exe_file.name),
            program_arguments.existing_path(
                existing_path_argument
            ),
            program_arguments.remaining_part_of_current_line_as_literal(text_until_end_of_line),
        ])

        def get_command_assertion(tcds: TestCaseDs) -> Assertion[Command]:
            symbols = SymbolTable.empty()
            return asrt_command.matches_command(
                asrt.anything_goes(),
                asrt.equals([
                    str(relativity_configurations.ATC_FILE
                        .named_file_conf(exe_file.name)
                        .path_sdv
                        .resolve(symbols)
                        .value_of_any_dependency__d(tcds)
                        .primitive
                        ),
                    str(existing_path_relativity
                        .named_file_conf(existing_path_argument.name)
                        .path_sdv
                        .resolve(symbols)
                        .value_of_any_dependency__d(tcds)
                        .primitive
                        ),
                    text_until_end_of_line,
                ])
            )

        act_instruction = instr([act_contents.as_str])
        executor_that_records_arguments = CommandExecutorThatRecordsArguments()
        # ACT & ASSERT #
        integration_check.check_execution(
            self,
            actor,
            [act_instruction],
            arrangement_w_tcds(
                process_execution=ProcessExecutionArrangement(
                    os_services=os_services_access.new_for_cmd_exe(executor_that_records_arguments)
                ),
                hds_contents=hds_populators.multiple([
                    relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                        fs.DirContents([exe_file])
                    ),
                    existing_path_relativity.populator_for_relativity_option_root__hds(
                        fs.DirContents([fs.File.empty(existing_path_argument.name)])
                    ),
                ])
            ),
            Expectation(
                after_execution=ExecutedCommandAssertion(
                    executor_that_records_arguments,
                    get_command_assertion,
                )
            ),
        )


class TestArgumentsOfInterpreterAndActAreConcatenated(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        actor = sut.actor(COMMAND_THAT_RUNS_PYTHON_PROGRAM_FILE)

        exe_file = fs.python_executable_file(
            'program-name',
            py_programs.exit_with_0()
        )
        argument_to_act_file = 'argument-to-act-file'
        act_contents = ab.sequence__r([
            ab.singleton(exe_file.name),
            ab.singleton(argument_to_act_file)
        ])
        interpreter_arguments_symbol = ListConstantSymbolContext('INTERPRETER_ARGS_LIST', ['1st', '2nd'])
        interpreter_arguments = ArgumentsSdv.new_without_validation(
            interpreter_arguments_symbol.sdv
        )
        actor = sut.actor(
            command_sdvs.for_executable_file(
                path_sdvs.constant(path_ddvs.absolute_file_name(sys.executable)),
                interpreter_arguments
            )
        )

        def get_command_assertion(tcds: TestCaseDs) -> Assertion[Command]:
            symbols = SymbolTable.empty()
            return asrt_command.matches_command(
                asrt.anything_goes(),
                asrt.equals(
                    interpreter_arguments_symbol.constant_list +
                    [
                        str(relativity_configurations.ATC_FILE
                            .named_file_conf(exe_file.name)
                            .path_sdv
                            .resolve(symbols)
                            .value_of_any_dependency__d(tcds)
                            .primitive
                            ),
                        argument_to_act_file,
                    ]
                )
            )

        act_instruction = instr([act_contents.as_str])
        executor_that_records_arguments = CommandExecutorThatRecordsArguments()
        # ACT & ASSERT #
        integration_check.check_execution(
            self,
            actor,
            [act_instruction],
            arrangement_w_tcds(
                process_execution=ProcessExecutionArrangement(
                    os_services=os_services_access.new_for_cmd_exe(executor_that_records_arguments)
                ),
                hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                    fs.DirContents([exe_file])
                )
            ),
            Expectation(
                after_execution=ExecutedCommandAssertion(
                    executor_that_records_arguments,
                    get_command_assertion,
                )
            ),
        )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
