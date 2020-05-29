import unittest

from exactly_lib.actors import file_interpreter as sut
from exactly_lib.test_case_file_structure.path_relativity import RelHdsOptionType, RelOptionType
from exactly_lib.type_system.logic.program.process_execution.command import Command
from exactly_lib.util.string import lines_content
from exactly_lib_test.actors.test_resources.act_phase_execution import Arrangement, Expectation, \
    check_execution
from exactly_lib_test.actors.test_resources.misc import PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN
from exactly_lib_test.execution.test_resources import eh_assertions
from exactly_lib_test.symbol.data.test_resources.path import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.symbol.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case.result.test_resources import svh_assertions
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_case_file_structure.test_resources.hds_populators import contents_in
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.py_program import \
    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES


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
            hds_contents=contents_in(RelHdsOptionType.REL_HDS_ACT, fs.DirContents([
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
            result_of_execute=eh_assertions.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=asrt.matches_sequence([
                symbol_for_source_file.reference_assertion__path_or_string(PATH_RELATIVITY_VARIANTS_FOR_FILE_TO_RUN),
                argument_symbol.reference_assertion__any_data_type,
            ]),
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
            result_of_execute=eh_assertions.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=asrt.matches_sequence([
                dir_symbol.reference_assertion__path_or_string,
                source_file_name_symbol.reference_assertion__path_component,
            ]),
        )
        self._check(command_line,
                    arrangement,
                    expectation)
