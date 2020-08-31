import pathlib
import sys
import unittest

from exactly_lib.actors import file_interpreter as sut
from exactly_lib.symbol.data import path_sdvs
from exactly_lib.symbol.logic.program.command_sdv import CommandSdv
from exactly_lib.test_case_file_structure.path_relativity import RelHdsOptionType, RelOptionType
from exactly_lib.test_case_utils.program.command import command_sdvs
from exactly_lib.type_system.data import paths
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.actors.test_resources import relativity_configurations
from exactly_lib_test.actors.test_resources.integration_check import Arrangement, Expectation, \
    check_execution, PostSdsExpectation
from exactly_lib_test.actors.test_resources.misc import PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.symbol.data.test_resources.path import ConstantSuffixPathDdvSymbolContext, PathSymbolContext
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case_file_structure.test_resources import hds_populators
from exactly_lib_test.test_case_file_structure.test_resources.hds_populators import contents_in
from exactly_lib_test.test_case_utils.test_resources.validation import pre_sds_validation_fails__svh
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import Dir
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as asrt_pr
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.py_program import \
    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES


def suite_for(command_that_runs_python_file: CommandSdv) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()

    ret_val.addTest(TestValidationShouldFailWhenInterpreterProgramFileDoesNotExist())
    ret_val.addTest(TestValidationShouldFailWhenInterpreterProgramFileIsADirectory())

    ret_val.addTest(TestValidationShouldFailWhenSourceFileDoesNotExist(command_that_runs_python_file))
    ret_val.addTest(TestValidationShouldFailWhenSourceFileIsADirectory(command_that_runs_python_file))

    ret_val.addTest(TestStringSymbolReferenceInInterpreter())
    ret_val.addTest(TestStringSymbolReferenceInSourceAndArgument(command_that_runs_python_file))
    ret_val.addTest(TestMultipleSymbolReferencesInSourceFileRef(command_that_runs_python_file))

    return ret_val


class TestCaseBase(unittest.TestCase):
    def __init__(self, command_that_runs_python_file: CommandSdv):
        super().__init__()
        self.command_that_runs_python_file = command_that_runs_python_file

    def shortDescription(self):
        return '{}, command={}'.format(
            str(type(self)),
            self.command_that_runs_python_file,
        )

    def _check(self,
               command_line: str,
               arrangement: Arrangement,
               expectation: Expectation):
        check_execution(self,
                        sut.actor(self.command_that_runs_python_file),
                        [instr([command_line])],
                        arrangement,
                        expectation)


class TestValidationShouldFailWhenSourceFileDoesNotExist(TestCaseBase):
    def runTest(self):
        command_line = 'non-existing-file.src'
        arrangement = Arrangement()

        expectation = Expectation(
            validation=pre_sds_validation_fails__svh()
        )
        self._check(command_line,
                    arrangement,
                    expectation)


class TestValidationShouldFailWhenSourceFileIsADirectory(TestCaseBase):
    def runTest(self):
        source_file = 'source-file.src'
        command_line = source_file
        arrangement = Arrangement(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, fs.DirContents([
                Dir.empty(source_file)]))
        )
        expectation = Expectation(
            validation=pre_sds_validation_fails__svh()
        )
        self._check(command_line,
                    arrangement,
                    expectation)


class TestStringSymbolReferenceInSourceAndArgument(TestCaseBase):
    def runTest(self):
        symbol_for_source_file = StringConstantSymbolContext('source_file_symbol_name',
                                                             'the-source-file.py')

        argument_symbol = StringConstantSymbolContext('argument_symbol_name', 'string-constant')

        expected_output = lines_content([argument_symbol.str_value])

        command_line = '{source_file} {argument} '.format(
            source_file=symbol_for_source_file.name__sym_ref_syntax,
            argument=argument_symbol.name__sym_ref_syntax,
        )

        arrangement = Arrangement(
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
                argument_symbol.reference_assertion__any_data_type,
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


class TestMultipleSymbolReferencesInSourceFileRef(TestCaseBase):
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

        arrangement = Arrangement(
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
                paths.absolute_path(pathlib.Path(sys.executable))
            ),
        )

        interpreter_with_symbol_reference = command_sdvs.for_executable_file(
            python_interpreter_symbol.reference_sdv__path_or_string(
                relativity_configurations.INTERPRETER_FILE.relativity
            )
        )

        arrangement = Arrangement(
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
                paths.rel_hds(relativity_configurations.INTERPRETER_FILE.relativity_option_rel_hds,
                              paths.constant_path_part('non-existing'))),
        )

        arrangement = Arrangement(
            hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                fs.DirContents([source_file])
            )
        )

        expectation = Expectation(
            validation=pre_sds_validation_fails__svh()
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
                paths.rel_hds(relativity_configurations.INTERPRETER_FILE.relativity_option_rel_hds,
                              paths.constant_path_part(a_dir.name))),
        )

        command_line = source_file
        arrangement = Arrangement(
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
            validation=pre_sds_validation_fails__svh()
        )
        # ACT & ASSERT #
        check_execution(self,
                        sut.actor(interpreter_with_program_that_is_a_dir),
                        [instr([command_line.name])],
                        arrangement,
                        expectation)
