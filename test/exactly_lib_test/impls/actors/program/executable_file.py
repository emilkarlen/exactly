import unittest
from contextlib import contextmanager
from typing import List, ContextManager

from exactly_lib.impls.actors.program import actor as sut
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.util.str_.misc_formatting import lines_content
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.impls.actors.program.test_resources import ConfigurationWithPythonProgramBase
from exactly_lib_test.impls.actors.test_resources import \
    test_validation_for_single_file, relativity_configurations
from exactly_lib_test.impls.actors.test_resources.action_to_check import suite_for_execution, TestCaseSourceSetup
from exactly_lib_test.impls.actors.test_resources.integration_check import Arrangement, Expectation, \
    check_execution, PostSdsExpectation
from exactly_lib_test.impls.actors.test_resources.misc import PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN
from exactly_lib_test.impls.test_resources.validation.svh_validation import ValidationExpectationSvh
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions import value_assertion_str as str_asrt
from exactly_lib_test.type_val_deps.types.list_.test_resources.list_ import ListConstantSymbolContext
from exactly_lib_test.type_val_deps.types.path.test_resources.path import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.util.test_resources.py_program import \
    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    configuration = TheConfiguration()

    ret_val.addTest(unittest.makeSuite(TestValidationErrorPreSds))
    ret_val.addTest(test_validation_for_single_file.suite_for(configuration))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulExecutionOfProgramRelHdsActWithCommandLineArguments))
    ret_val.addTest(unittest.makeSuite(TestSymbolUsages))
    ret_val.addTest(suite_for_execution(configuration))
    return ret_val


class TheConfiguration(ConfigurationWithPythonProgramBase):
    @contextmanager
    def _instructions_for_executing_py_source(self, py_src: List[str]) -> ContextManager[TestCaseSourceSetup]:
        exe_file = fs.python_executable_file('the-program',
                                             lines_content(py_src))

        yield TestCaseSourceSetup(
            act_phase_instructions=[instr([exe_file.name])],
            home_act_dir_contents=DirContents([exe_file])
        )


class TestValidationErrorPreSds(unittest.TestCase):
    def test_executable_file_must_exist(self):
        act_phase_instructions = [
            instr(['non-existing-executable'])
        ]
        arrangement = Arrangement()
        expectation = Expectation(
            validation=ValidationExpectationSvh.fails__pre_sds()
        )
        check_execution(self,
                        sut.actor(),
                        act_phase_instructions,
                        arrangement,
                        expectation)

    def test_executable_file_must_be_executable(self):
        executable_file_name = 'existing-executable'
        act_phase_instructions = [
            instr([executable_file_name])
        ]
        arrangement = Arrangement(
            hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                fs.DirContents([File.empty(executable_file_name)]))
        )
        expectation = Expectation(
            validation=ValidationExpectationSvh.fails__pre_sds()
        )
        check_execution(self,
                        sut.actor(),
                        act_phase_instructions,
                        arrangement,
                        expectation)


class TestSuccessfulExecutionOfProgramRelHdsActWithCommandLineArguments(unittest.TestCase):
    def runTest(self):
        actor = sut.actor()
        act_phase_instructions = [
            instr(['system-under-test first-argument "quoted argument"'])
        ]
        arrangement = Arrangement(
            hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                fs.DirContents([
                    fs.python_executable_file(
                        'system-under-test',
                        PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
                ])))
        expected_output = lines_content(['first-argument',
                                         'quoted argument'])
        expectation = Expectation(
            execute=eh_assertions.is_exit_code(0),
            post_sds=PostSdsExpectation.constant(
                sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                      'CLI arguments, one per line')))
        )
        check_execution(self,
                        actor,
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
            hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                fs.DirContents([
                    fs.python_executable_file(
                        executable,
                        PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
                ])),
            symbol_table=list_symbol.symbol_table
        )

        expectation = Expectation(
            symbol_usages=asrt.matches_singleton_sequence(list_symbol.reference_assertion),
            execute=eh_assertions.is_exit_code(0),
            post_sds=PostSdsExpectation.constant(
                sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                      'CLI arguments, one per line'))
            ),
        )
        check_execution(self,
                        sut.actor(),
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
            hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                fs.DirContents([
                    fs.python_executable_file(
                        executable,
                        PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
                ])),
            symbol_table=symbol.symbol_table
        )

        expectation = Expectation(
            execute=eh_assertions.is_exit_code(0),
            symbol_usages=asrt.matches_singleton_sequence(symbol.reference_assertion__any_data_type),
            post_sds=PostSdsExpectation.constant(
                sub_process_result_from_execute=pr.stdout(str_asrt.contains(file_name_of_referenced_file))
            ),
        )

        check_execution(self,
                        sut.actor(),
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
            hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                fs.DirContents([
                    fs.python_executable_file(
                        symbol_for_executable.str_value,
                        PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
                ])),
            symbol_table=symbol_for_executable.symbol_table
        )

        expectation = Expectation(
            execute=eh_assertions.is_exit_code(0),
            symbol_usages=asrt.matches_sequence([
                symbol_for_executable.reference_assertion__path_or_string(PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN),
            ]
            ),
            post_sds=PostSdsExpectation.constant(
                sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                      'CLI arguments, one per line'))
            ),
        )
        check_execution(self,
                        sut.actor(),
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
            hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                fs.DirContents([
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
            execute=eh_assertions.is_exit_code(0),
            symbol_usages=asrt.matches_sequence([
                symbol_for_executable.reference_assertion__path_or_string(PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN),
                argument_symbol.reference_assertion__any_data_type,
            ]),
            post_sds=PostSdsExpectation.constant(
                sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                      'CLI arguments, one per line'))
            ),
        )
        check_execution(self,
                        sut.actor(),
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
            hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                fs.DirContents([
                    fs.Dir(sub_dir_of_home, [executable_file])
                ])
            ),
            symbol_table=SymbolContext.symbol_table_of_contexts([
                dir_symbol,
                executable_file_name_symbol,
            ])
        )

        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                dir_symbol.reference_assertion__path_or_string,
                executable_file_name_symbol.reference_assertion__string_made_up_of_just_strings,
            ]),
            execute=eh_assertions.is_exit_code(0),
            post_sds=PostSdsExpectation.constant(
                sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                      'CLI arguments, one per line'))
            ),
        )
        check_execution(self,
                        sut.actor(),
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
            hds_contents=relativity_configurations.ATC_FILE.populator_for_relativity_option_root__hds(
                fs.DirContents([
                    fs.python_executable_file(
                        executable_file_name,
                        PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
                ])
            ),
            symbol_table=symbol.symbol_table
        )

        expectation = Expectation(
            symbol_usages=asrt.matches_sequence(
                [symbol.reference_assertion__any_data_type]
            ),
            execute=eh_assertions.is_exit_code(0),
            post_sds=PostSdsExpectation.constant(
                sub_process_result_from_execute=pr.stdout(
                    asrt.Equals(expected_output,
                                'CLI arguments, one per line')
                )
            ),
        )
        check_execution(self,
                        sut.actor(),
                        [instr([command_line])],
                        arrangement,
                        expectation)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
