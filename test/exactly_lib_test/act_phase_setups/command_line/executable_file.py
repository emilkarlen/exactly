import pathlib
import unittest
from contextlib import contextmanager

from exactly_lib.act_phase_setups import command_line as sut
from exactly_lib.instructions.utils.arg_parse.parse_file_ref import path_or_string_reference_restrictions, \
    PATH_COMPONENT_STRING_REFERENCES_RESTRICTION
from exactly_lib.instructions.utils.arg_parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.restrictions.reference_restrictions import no_restrictions
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.type_system_values import file_refs
from exactly_lib.type_system_values.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.act_phase_setups.test_resources import py_program
from exactly_lib_test.act_phase_setups.test_resources import \
    test_validation_for_single_file_rel_home as single_file_rel_home
from exactly_lib_test.act_phase_setups.test_resources.act_phase_execution import Arrangement, Expectation, \
    check_execution
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import Configuration, \
    suite_for_execution, TestCaseSourceSetup
from exactly_lib_test.act_phase_setups.test_resources.py_program import \
    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES
from exactly_lib_test.execution.test_resources import eh_check
from exactly_lib_test.instructions.test_resources.assertion_utils import svh_check
from exactly_lib_test.symbol.test_resources import symbol_utils as su
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.file_utils import tmp_file_containing_lines
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as str_asrt
from exactly_lib_test.type_system_values.test_resources import list_values as lv


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    configuration = TheConfiguration()

    ret_val.addTest(unittest.makeSuite(TestInvalidSyntax))
    ret_val.addTest(single_file_rel_home.suite_for(configuration))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulExecutionOfProgramRelHomeWithCommandLineArguments))
    ret_val.addTest(unittest.makeSuite(TestSymbolUsages))
    ret_val.addTest(suite_for_execution(configuration))
    return ret_val


class TheConfiguration(Configuration):
    def __init__(self):
        super().__init__(sut.Constructor())

    @contextmanager
    def program_that_copes_stdin_to_stdout(self, home_dir_path: pathlib.Path) -> list:
        return self._instructions_for_executing_source_from_py_file(py_program.copy_stdin_to_stdout())

    @contextmanager
    def program_that_prints_to_stderr(self, home_dir_path: pathlib.Path, string_to_print: str) -> list:
        return self._instructions_for_executing_source_from_py_file(py_program.write_string_to_stderr(string_to_print))

    @contextmanager
    def program_that_prints_to_stdout(self, home_dir_path: pathlib.Path, string_to_print: str) -> list:
        return self._instructions_for_executing_source_from_py_file(py_program.write_string_to_stdout(string_to_print))

    @contextmanager
    def program_that_exits_with_code(self, home_dir_path: pathlib.Path, exit_code: int) -> list:
        return self._instructions_for_executing_source_from_py_file(py_program.exit_with_code(exit_code))

    @contextmanager
    def program_that_prints_cwd_without_new_line_to_stdout(self, home_dir_path: pathlib.Path) -> list:
        return self._instructions_for_executing_source_from_py_file(py_program.write_cwd_to_stdout())

    @contextmanager
    def program_that_prints_value_of_environment_variable_to_stdout(self, home_dir_path: pathlib.Path,
                                                                    var_name: str) -> list:
        return self._instructions_for_executing_source_from_py_file(
            py_program.write_value_of_environment_variable_to_stdout(var_name))

    @contextmanager
    def program_that_sleeps_at_least(self, number_of_seconds: int) -> TestCaseSourceSetup:
        statements = py_program.program_that_sleeps_at_least_and_then_exists_with_zero_exit_status(number_of_seconds)
        with tmp_file_containing_lines(statements) as src_path:
            yield TestCaseSourceSetup(_instructions_for_executing_py_file(src_path))

    def _instructions_for_executing_source_from_py_file(self, statements: list) -> list:
        with tmp_file_containing_lines(statements) as src_path:
            yield _instructions_for_executing_py_file(src_path)


def _instructions_for_executing_py_file(src_path: pathlib.Path) -> list:
    cmd = py_exe.command_line_for_interpreting(src_path)
    return [instr([cmd])]


class TestInvalidSyntax(unittest.TestCase):
    def test_executable_file_must_exist(self):
        act_phase_instructions = [
            instr(['non-existing-executable'])
        ]
        arrangement = Arrangement(act_phase_instructions)
        expectation = Expectation(
            result_of_validate_pre_sds=svh_check.is_validation_error()
        )
        check_execution(self, sut.Constructor(),
                        arrangement,
                        expectation)

    def test_executable_file_must_be_executable(self):
        executable_file_name = 'existing-executable'
        act_phase_instructions = [
            instr([executable_file_name])
        ]
        arrangement = Arrangement(
            act_phase_instructions,
            home_dir_contents=fs.DirContents([fs.empty_file(executable_file_name)])
        )
        expectation = Expectation(
            result_of_validate_pre_sds=svh_check.is_validation_error()
        )
        check_execution(self, sut.Constructor(),
                        arrangement,
                        expectation)


class TestSuccessfulExecutionOfProgramRelHomeWithCommandLineArguments(unittest.TestCase):
    def runTest(self):
        executor_constructor = sut.Constructor()
        act_phase_instructions = [
            instr(['system-under-test first-argument "quoted argument"'])
        ]
        arrangement = Arrangement(act_phase_instructions,
                                  home_dir_contents=fs.DirContents([
                                      fs.python_executable_file(
                                          'system-under-test',
                                          PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
                                  ]))
        expected_output = lines_content(['first-argument',
                                         'quoted argument'])
        expectation = Expectation(result_of_execute=eh_check.is_exit_code(0),
                                  sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                                        'CLI arguments, one per line')))
        check_execution(self, executor_constructor,
                        arrangement, expectation)


class TestSymbolUsages(unittest.TestCase):
    def test_symbol_reference_in_arguments(self):
        list_symbol = NameAndValue('list_symbol_name', ['first element',
                                                        'second element'])

        string_constant = 'string-constant'

        expected_output = lines_content(['string-constant'] + list_symbol.value)

        executable = 'the-executable'

        command_line = '{executable} {string_constant} {list_symbol}'.format(
            executable=executable,
            string_constant=string_constant,
            list_symbol=symbol_reference_syntax_for_name(list_symbol.name),
        )

        arrangement = Arrangement(
            [instr([command_line])],
            home_dir_contents=fs.DirContents([
                fs.python_executable_file(
                    executable,
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ]),
            symbol_table=SymbolTable({
                list_symbol.name:
                    su.list_value_constant_container(lv.list_value_of_string_constants(list_symbol.value)),
            })
        )

        expectation = Expectation(
            result_of_execute=eh_check.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=equals_symbol_references(
                [SymbolReference(list_symbol.name, no_restrictions())]
            )
        )
        check_execution(self,
                        sut.Constructor(),
                        arrangement,
                        expectation)

    def test_possibility_to_have_sds_file_references_in_argument(self):
        file_name_of_referenced_file = 'file-name.txt'
        symbol = NameAndValue('symbol_name',
                              file_refs.of_rel_option(RelOptionType.REL_TMP,
                                                      PathPartAsFixedPath(file_name_of_referenced_file)))

        executable = 'the-executable'

        command_line = '{executable} {symbol}'.format(
            executable=executable,
            symbol=symbol_reference_syntax_for_name(symbol.name),
        )

        arrangement = Arrangement(
            [instr([command_line])],
            home_dir_contents=fs.DirContents([
                fs.python_executable_file(
                    executable,
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ]),
            symbol_table=SymbolTable({
                symbol.name:
                    su.file_ref_constant_container(symbol.value),
            })
        )

        expectation = Expectation(
            result_of_execute=eh_check.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(str_asrt.contains(file_name_of_referenced_file)),
            symbol_usages=equals_symbol_references(
                [SymbolReference(symbol.name, no_restrictions())]
            )
        )
        check_execution(self,
                        sut.Constructor(),
                        arrangement,
                        expectation)

    def test_string_symbol_reference_in_executable(self):
        symbol_for_executable = NameAndValue('executable_symbol_name', 'the-executable')

        string_constant = 'string-constant'

        expected_output = lines_content(['string-constant'])

        command_line = '{executable} {string_constant} '.format(
            executable=symbol_reference_syntax_for_name(symbol_for_executable.name),
            string_constant=string_constant,
        )

        arrangement = Arrangement(
            [instr([command_line])],
            home_dir_contents=fs.DirContents([
                fs.python_executable_file(
                    symbol_for_executable.value,
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ]),
            symbol_table=SymbolTable({
                symbol_for_executable.name:
                    su.string_value_constant_container(symbol_for_executable.value),
            })
        )

        expectation = Expectation(
            result_of_execute=eh_check.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=equals_symbol_references([
                SymbolReference(symbol_for_executable.name,
                                path_or_string_reference_restrictions(PATH_RELATIVITY_VARIANTS_FOR_EXECUTABLE)),
            ]
            )
        )
        check_execution(self,
                        sut.Constructor(),
                        arrangement,
                        expectation)

    def test_string_symbol_reference_in_executable_and_argument(self):
        symbol_for_executable = NameAndValue('executable_symbol_name', 'the-executable')

        argument_symbol = NameAndValue('argument_symbol_name', 'string-constant')

        expected_output = lines_content([argument_symbol.value])

        command_line = '{executable} {argument} '.format(
            executable=symbol_reference_syntax_for_name(symbol_for_executable.name),
            argument=symbol_reference_syntax_for_name(argument_symbol.name),
        )

        arrangement = Arrangement(
            [instr([command_line])],
            home_dir_contents=fs.DirContents([
                fs.python_executable_file(
                    symbol_for_executable.value,
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ]),
            symbol_table=SymbolTable({
                symbol_for_executable.name:
                    su.string_value_constant_container(symbol_for_executable.value),
                argument_symbol.name:
                    su.string_value_constant_container(argument_symbol.value),
            })
        )

        expectation = Expectation(
            result_of_execute=eh_check.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=equals_symbol_references([
                SymbolReference(symbol_for_executable.name,
                                path_or_string_reference_restrictions(PATH_RELATIVITY_VARIANTS_FOR_EXECUTABLE)),
                SymbolReference(argument_symbol.name, no_restrictions()),
            ]),
        )
        check_execution(self,
                        sut.Constructor(),
                        arrangement,
                        expectation)

    def test_multiple_symbol_references_in_executable(self):
        sub_dir_of_home = 'sub-dir'
        dir_symbol = NameAndValue('dir_symbol_name',
                                  file_refs.rel_home(PathPartAsFixedPath(sub_dir_of_home)))

        executable_file_name_symbol = NameAndValue('executable_file_name_symbol_name',
                                                   'the-executable-file')

        argument = 'argument_string'

        expected_output = lines_content([argument])

        command_line = '{dir}/{file_name}  {argument} '.format(
            dir=symbol_reference_syntax_for_name(dir_symbol.name),
            file_name=symbol_reference_syntax_for_name(executable_file_name_symbol.name),
            argument=argument,
        )

        executable_file = fs.python_executable_file(
            executable_file_name_symbol.value,
            PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)

        arrangement = Arrangement(
            [instr([command_line])],
            home_dir_contents=fs.DirContents([
                fs.Dir(sub_dir_of_home, [executable_file])
            ]),
            symbol_table=SymbolTable({
                dir_symbol.name:
                    su.file_ref_constant_container(dir_symbol.value),

                executable_file_name_symbol.name:
                    su.string_value_constant_container(executable_file_name_symbol.value),
            })
        )

        expectation = Expectation(
            result_of_execute=eh_check.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=equals_symbol_references([
                SymbolReference(dir_symbol.name,
                                path_or_string_reference_restrictions(PATH_RELATIVITY_VARIANTS_FOR_EXECUTABLE)),

                SymbolReference(executable_file_name_symbol.name,
                                PATH_COMPONENT_STRING_REFERENCES_RESTRICTION),
            ]),
        )
        check_execution(self,
                        sut.Constructor(),
                        arrangement,
                        expectation)


PATH_RELATIVITY_VARIANTS_FOR_EXECUTABLE = PathRelativityVariants({RelOptionType.REL_HOME},
                                                                 absolute=True)

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
