import pathlib
import unittest
from contextlib import contextmanager
from typing import List

from exactly_lib.actors import command_line as sut
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, RelHdsOptionType
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.actors.test_resources import \
    test_validation_for_single_file_rel_hds_act as single_file_rel_home
from exactly_lib_test.actors.test_resources.act_phase_execution import Arrangement, Expectation, \
    check_execution
from exactly_lib_test.actors.test_resources.action_to_check import Configuration, \
    suite_for_execution, TestCaseSourceSetup
from exactly_lib_test.actors.test_resources.misc import PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.symbol.data.test_resources.list_ import ListConstantSymbolContext
from exactly_lib_test.symbol.data.test_resources.path import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case.result.test_resources import svh_assertions
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case_file_structure.test_resources.hds_populators import contents_in
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import File
from exactly_lib_test.test_resources.files.file_utils import tmp_file_containing_lines
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as str_asrt
from exactly_lib_test.util.test_resources import py_program
from exactly_lib_test.util.test_resources.py_program import \
    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    configuration = TheConfiguration()

    ret_val.addTest(unittest.makeSuite(TestValidationErrorPreSds))
    ret_val.addTest(single_file_rel_home.suite_for(configuration))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulExecutionOfProgramRelHdsActWithCommandLineArguments))
    ret_val.addTest(unittest.makeSuite(TestSymbolUsages))
    ret_val.addTest(suite_for_execution(configuration))
    return ret_val


class TheConfiguration(Configuration):
    def __init__(self):
        super().__init__(sut.Parser())

    @contextmanager
    def program_that_copes_stdin_to_stdout(self, hds: HomeDirectoryStructure) -> List[ActPhaseInstruction]:
        return self._instructions_for_executing_source_from_py_file(py_program.copy_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self,
                                      hds: HomeDirectoryStructure,
                                      string_to_print: str) -> List[ActPhaseInstruction]:
        return self._instructions_for_executing_source_from_py_file(py_program.write_string_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self,
                                      hds: HomeDirectoryStructure,
                                      string_to_print: str) -> List[ActPhaseInstruction]:
        return self._instructions_for_executing_source_from_py_file(py_program.write_string_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self,
                                     hds: HomeDirectoryStructure,
                                     exit_code: int) -> List[ActPhaseInstruction]:
        return self._instructions_for_executing_source_from_py_file(py_program.exit_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self,
                                                           hds: HomeDirectoryStructure,
                                                           ) -> List[ActPhaseInstruction]:
        return self._instructions_for_executing_source_from_py_file(py_program.write_cwd_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, hds: HomeDirectoryStructure,
                                                                    var_name: str,
                                                                    ) -> List[ActPhaseInstruction]:
        return self._instructions_for_executing_source_from_py_file(
            py_program.write_value_of_environment_variable_to_stdout(var_name))

    @contextmanager
    def program_that_sleeps_at_least(self, number_of_seconds: int) -> TestCaseSourceSetup:
        statements = py_program.program_that_sleeps_at_least_and_then_exists_with_zero_exit_status(number_of_seconds)
        with tmp_file_containing_lines(statements) as src_path:
            yield TestCaseSourceSetup(act_phase_instructions=_instructions_for_executing_py_file(src_path))

    def _instructions_for_executing_source_from_py_file(self, statements: list) -> list:
        with tmp_file_containing_lines(statements) as src_path:
            yield _instructions_for_executing_py_file(src_path)


def _instructions_for_executing_py_file(src_path: pathlib.Path) -> list:
    cmd = py_exe.command_line_for_interpreting(src_path)
    return [instr([cmd])]


class TestValidationErrorPreSds(unittest.TestCase):
    def test_executable_file_must_exist(self):
        act_phase_instructions = [
            instr(['non-existing-executable'])
        ]
        arrangement = Arrangement()
        expectation = Expectation(
            result_of_validate_pre_sds=svh_assertions.is_validation_error()
        )
        check_execution(self,
                        sut.Parser(),
                        act_phase_instructions,
                        arrangement,
                        expectation)

    def test_executable_file_must_be_executable(self):
        executable_file_name = 'existing-executable'
        act_phase_instructions = [
            instr([executable_file_name])
        ]
        arrangement = Arrangement(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT,
                                     fs.DirContents([File.empty(executable_file_name)]))
        )
        expectation = Expectation(
            result_of_validate_pre_sds=svh_assertions.is_validation_error()
        )
        check_execution(self,
                        sut.Parser(),
                        act_phase_instructions,
                        arrangement,
                        expectation)


class TestSuccessfulExecutionOfProgramRelHdsActWithCommandLineArguments(unittest.TestCase):
    def runTest(self):
        executor_constructor = sut.Parser()
        act_phase_instructions = [
            instr(['system-under-test first-argument "quoted argument"'])
        ]
        arrangement = Arrangement(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, fs.DirContents([
                fs.python_executable_file(
                    'system-under-test',
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ])))
        expected_output = lines_content(['first-argument',
                                         'quoted argument'])
        expectation = Expectation(result_of_execute=eh_assertions.is_exit_code(0),
                                  sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                                        'CLI arguments, one per line')))
        check_execution(self,
                        executor_constructor,
                        act_phase_instructions,
                        arrangement,
                        expectation)


class TestSymbolUsages(unittest.TestCase):
    def test_symbol_reference_in_arguments(self):
        list_symbol = ListConstantSymbolContext('list_symbol_name', ['first element',
                                                                     'second element'])

        string_constant = 'string-constant'

        expected_output = lines_content(['string-constant'] + list_symbol.constant_list)

        executable = 'the-executable'

        command_line = '{executable} {string_constant} {list_symbol}'.format(
            executable=executable,
            string_constant=string_constant,
            list_symbol=list_symbol.name__sym_ref_syntax,
        )

        arrangement = Arrangement(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, fs.DirContents([
                fs.python_executable_file(
                    executable,
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ])),
            symbol_table=list_symbol.symbol_table
        )

        expectation = Expectation(
            result_of_execute=eh_assertions.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=asrt.matches_singleton_sequence(list_symbol.reference_assertion)
        )
        check_execution(self,
                        sut.Parser(),
                        [instr([command_line])],
                        arrangement,
                        expectation)

    def test_possibility_to_have_sds_path_references_in_argument(self):
        file_name_of_referenced_file = 'file-name.txt'
        symbol = ConstantSuffixPathDdvSymbolContext('symbol_name',
                                                    RelOptionType.REL_TMP,
                                                    file_name_of_referenced_file)

        executable = 'the-executable'

        command_line = '{executable} {symbol}'.format(
            executable=executable,
            symbol=symbol.name__sym_ref_syntax,
        )

        arrangement = Arrangement(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, fs.DirContents([
                fs.python_executable_file(
                    executable,
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ])),
            symbol_table=symbol.symbol_table
        )

        expectation = Expectation(
            result_of_execute=eh_assertions.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(str_asrt.contains(file_name_of_referenced_file)),
            symbol_usages=asrt.matches_singleton_sequence(symbol.reference_assertion__any_data_type)
        )

        check_execution(self,
                        sut.Parser(),
                        [instr([command_line])],
                        arrangement,
                        expectation)

    def test_string_symbol_reference_in_executable(self):
        symbol_for_executable = StringConstantSymbolContext('executable_symbol_name', 'the-executable')

        string_constant = 'string-constant'

        expected_output = lines_content(['string-constant'])

        command_line = '{executable} {string_constant} '.format(
            executable=symbol_for_executable.name__sym_ref_syntax,
            string_constant=string_constant,
        )

        arrangement = Arrangement(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, fs.DirContents([
                fs.python_executable_file(
                    symbol_for_executable.str_value,
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ])),
            symbol_table=symbol_for_executable.symbol_table
        )

        expectation = Expectation(
            result_of_execute=eh_assertions.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=asrt.matches_sequence([
                symbol_for_executable.reference_assertion__path_or_string(PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN),
            ]
            )
        )
        check_execution(self,
                        sut.Parser(),
                        [instr([command_line])],
                        arrangement,
                        expectation)

    def test_string_symbol_reference_in_executable_and_argument(self):
        symbol_for_executable = StringConstantSymbolContext('executable_symbol_name', 'the-executable')

        argument_symbol = StringConstantSymbolContext('argument_symbol_name', 'string-constant')

        expected_output = lines_content([argument_symbol.str_value])

        command_line = '{executable} {argument} '.format(
            executable=symbol_for_executable.name__sym_ref_syntax,
            argument=argument_symbol.name__sym_ref_syntax,
        )

        arrangement = Arrangement(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, fs.DirContents([
                fs.python_executable_file(
                    symbol_for_executable.str_value,
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ])),
            symbol_table=SymbolContext.symbol_table_of_contexts([
                symbol_for_executable,
                argument_symbol,
            ])
        )

        expectation = Expectation(
            result_of_execute=eh_assertions.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=asrt.matches_sequence([
                symbol_for_executable.reference_assertion__path_or_string(PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN),
                argument_symbol.reference_assertion__any_data_type,
            ]),
        )
        check_execution(self,
                        sut.Parser(),
                        [instr([command_line])],
                        arrangement,
                        expectation)

    def test_multiple_symbol_references_in_executable(self):
        sub_dir_of_home = 'sub-dir'
        dir_symbol = ConstantSuffixPathDdvSymbolContext('dir_symbol_name',
                                                        RelOptionType.REL_HDS_ACT,
                                                        sub_dir_of_home,
                                                        PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN)

        executable_file_name_symbol = StringConstantSymbolContext('executable_file_name_symbol_name',
                                                                  'the-executable-file')

        argument = 'argument_string'

        expected_output = lines_content([argument])

        command_line = '{dir}/{file_name}  {argument} '.format(
            dir=dir_symbol.name__sym_ref_syntax,
            file_name=executable_file_name_symbol.name__sym_ref_syntax,
            argument=argument,
        )

        executable_file = fs.python_executable_file(
            executable_file_name_symbol.str_value,
            PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)

        arrangement = Arrangement(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, fs.DirContents([
                fs.Dir(sub_dir_of_home, [executable_file])
            ])),
            symbol_table=SymbolContext.symbol_table_of_contexts([
                dir_symbol,
                executable_file_name_symbol,
            ])
        )

        expectation = Expectation(
            result_of_execute=eh_assertions.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=asrt.matches_sequence([
                dir_symbol.reference_assertion__path_or_string,
                executable_file_name_symbol.reference_assertion__string_made_up_of_just_strings,
            ]),
        )
        check_execution(self,
                        sut.Parser(),
                        [instr([command_line])],
                        arrangement,
                        expectation)

    def test_symbol_value_with_space_SHOULD_be_given_as_single_argument_to_program(self):
        symbol = StringConstantSymbolContext('symbol_name', 'symbol value with space')

        expected_output = lines_content([symbol.str_value])

        executable_file_name = 'the-executable_file_name'

        command_line = '{executable_file_name} {symbol}'.format(
            executable_file_name=executable_file_name,
            symbol=symbol.name__sym_ref_syntax,
        )

        arrangement = Arrangement(
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, fs.DirContents([
                fs.python_executable_file(
                    executable_file_name,
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ])),
            symbol_table=symbol.symbol_table
        )

        expectation = Expectation(
            result_of_execute=eh_assertions.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=asrt.matches_sequence(
                [symbol.reference_assertion__any_data_type]
            )
        )
        check_execution(self,
                        sut.Parser(),
                        [instr([command_line])],
                        arrangement,
                        expectation)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
