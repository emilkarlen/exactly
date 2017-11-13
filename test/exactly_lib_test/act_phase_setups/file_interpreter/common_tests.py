import unittest

from exactly_lib.act_phase_setups import file_interpreter as sut
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import RelHomeOptionType
from exactly_lib.test_case_utils.parse.parse_file_ref import path_or_string_reference_restrictions, \
    PATH_COMPONENT_STRING_REFERENCES_RESTRICTION
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.util.process_execution.os_process_execution import Command
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.act_phase_setups.test_resources.act_phase_execution import Arrangement, Expectation, \
    check_execution
from exactly_lib_test.act_phase_setups.test_resources.misc import PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils as su
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case_file_structure.test_resources.home_populators import contents_in
from exactly_lib_test.test_case_utils.test_resources import svh_assertions
from exactly_lib_test.test_case_utils.test_resources.py_program import \
    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(command_that_runs_python_file: Command) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()

    ret_val.addTest(TestValidationShouldFailWhenSourceFileDoesNotExist(command_that_runs_python_file))
    ret_val.addTest(TestValidationShouldFailWhenSourceFileIsADirectory(command_that_runs_python_file))

    ret_val.addTest(TestStringSymbolReferenceInSourceAndArgument(command_that_runs_python_file))
    ret_val.addTest(TestMultipleSymbolReferencesInSourceFileRef(command_that_runs_python_file))

    return ret_val


class TestCaseBase(unittest.TestCase):
    def __init__(self, command_that_runs_python_file: Command):
        super().__init__()
        self.command_that_runs_python_file = command_that_runs_python_file

    def shortDescription(self):
        return '{}, is_shell={}'.format(
            str(type(self)),
            self.command_that_runs_python_file.shell,
        )

    def _check(self,
               command_line: str,
               arrangement: Arrangement,
               expectation: Expectation):
        check_execution(self,
                        sut.constructor(self.command_that_runs_python_file),
                        [instr([command_line])],
                        arrangement,
                        expectation)


class TestValidationShouldFailWhenSourceFileDoesNotExist(TestCaseBase):
    def runTest(self):
        command_line = 'non-existing-file.src'
        arrangement = Arrangement()

        expectation = Expectation(
            result_of_validate_pre_sds=svh_assertions.is_validation_error()
        )
        self._check(command_line,
                    arrangement,
                    expectation)


class TestValidationShouldFailWhenSourceFileIsADirectory(TestCaseBase):
    def runTest(self):
        source_file = 'source-file.src'
        command_line = source_file
        arrangement = Arrangement(
            hds_contents=contents_in(RelHomeOptionType.REL_HOME_ACT, fs.DirContents([
                fs.empty_dir(source_file)]))
        )
        expectation = Expectation(
            result_of_validate_pre_sds=svh_assertions.is_validation_error()
        )
        self._check(command_line,
                    arrangement,
                    expectation)


class TestStringSymbolReferenceInSourceAndArgument(TestCaseBase):
    def runTest(self):
        symbol_for_source_file = NameAndValue('source_file_symbol_name',
                                              'the-source-file.py')

        argument_symbol = NameAndValue('argument_symbol_name', 'string-constant')

        expected_output = lines_content([argument_symbol.value])

        command_line = '{source_file} {argument} '.format(
            source_file=symbol_reference_syntax_for_name(symbol_for_source_file.name),
            argument=symbol_reference_syntax_for_name(argument_symbol.name),
        )

        arrangement = Arrangement(
            hds_contents=contents_in(RelHomeOptionType.REL_HOME_ACT, fs.DirContents([
                fs.File(
                    symbol_for_source_file.value,
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ])),
            symbol_table=SymbolTable({
                symbol_for_source_file.name:
                    su.string_constant_container(symbol_for_source_file.value),
                argument_symbol.name:
                    su.string_constant_container(argument_symbol.value),
            })
        )

        expectation = Expectation(
            result_of_execute=eh_assertions.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=equals_symbol_references([
                SymbolReference(symbol_for_source_file.name,
                                path_or_string_reference_restrictions(PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN)),
                SymbolReference(argument_symbol.name,
                                is_any_data_type()),
            ]),
        )
        self._check(command_line,
                    arrangement,
                    expectation)


class TestMultipleSymbolReferencesInSourceFileRef(TestCaseBase):
    def runTest(self):
        sub_dir_of_home = 'sub-dir'
        dir_symbol = NameAndValue('dir_symbol_name',
                                  file_refs.rel_home_act(PathPartAsFixedPath(sub_dir_of_home)))

        source_file_name_symbol = NameAndValue('source_file_name_symbol_name',
                                               'the-source-file.py')

        argument = 'argument_string'

        expected_output = lines_content([argument])

        command_line = '{dir}/{file_name}  {argument} '.format(
            dir=symbol_reference_syntax_for_name(dir_symbol.name),
            file_name=symbol_reference_syntax_for_name(source_file_name_symbol.name),
            argument=argument,
        )

        executable_file = fs.File(
            source_file_name_symbol.value,
            PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)

        arrangement = Arrangement(
            hds_contents=contents_in(RelHomeOptionType.REL_HOME_ACT, fs.DirContents([
                fs.Dir(sub_dir_of_home, [executable_file])
            ])),
            symbol_table=SymbolTable({
                dir_symbol.name:
                    su.file_ref_constant_container(dir_symbol.value),

                source_file_name_symbol.name:
                    su.string_constant_container(source_file_name_symbol.value),
            })
        )

        expectation = Expectation(
            result_of_execute=eh_assertions.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=equals_symbol_references([
                SymbolReference(dir_symbol.name,
                                path_or_string_reference_restrictions(PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN)),

                SymbolReference(source_file_name_symbol.name,
                                PATH_COMPONENT_STRING_REFERENCES_RESTRICTION),
            ]),
        )
        self._check(command_line,
                    arrangement,
                    expectation)
