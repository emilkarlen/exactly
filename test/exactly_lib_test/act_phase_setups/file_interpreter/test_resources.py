import unittest

from exactly_lib.act_phase_setups import file_interpreter as sut
from exactly_lib.instructions.utils.arg_parse.parse_file_ref import path_or_string_reference_restrictions
from exactly_lib.instructions.utils.arg_parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.symbol.restrictions.reference_restrictions import no_restrictions
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.util.process_execution.os_process_execution import Command
from exactly_lib.util.string import lines_content
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.act_phase_setups.test_resources.act_phase_execution import Arrangement, Expectation, \
    check_execution
from exactly_lib_test.act_phase_setups.test_resources.py_program import \
    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES
from exactly_lib_test.execution.test_resources import eh_check
from exactly_lib_test.symbol.test_resources import symbol_utils as su
from exactly_lib_test.symbol.test_resources.symbol_reference_assertions import equals_symbol_references
from exactly_lib_test.test_case.test_resources.act_phase_instruction import instr
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import process_result_assertions as pr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(command_that_runs_python_file: Command) -> unittest.TestSuite:
    ret_val = unittest.TestSuite()

    ret_val.addTest(TestStringSymbolReferenceInSourceAndArgument(command_that_runs_python_file))

    return ret_val


class TestStringSymbolReferenceInSourceAndArgument(unittest.TestCase):
    def __init__(self, command_that_runs_python_file: Command):
        super().__init__()
        self.command_that_runs_python_file = command_that_runs_python_file

    def shortDescription(self):
        return '{}, is_shell={}'.format(
            str(type(self)),
            self.command_that_runs_python_file.shell,
        )

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
            [instr([command_line])],
            home_dir_contents=fs.DirContents([
                fs.File(
                    symbol_for_source_file.value,
                    PYTHON_PROGRAM_THAT_PRINTS_COMMAND_LINE_ARGUMENTS_ON_SEPARATE_LINES)
            ]),
            symbol_table=SymbolTable({
                symbol_for_source_file.name:
                    su.string_value_constant_container(symbol_for_source_file.value),
                argument_symbol.name:
                    su.string_value_constant_container(argument_symbol.value),
            })
        )

        expectation = Expectation(
            result_of_execute=eh_check.is_exit_code(0),
            sub_process_result_from_execute=pr.stdout(asrt.Equals(expected_output,
                                                                  'CLI arguments, one per line')),
            symbol_usages=equals_symbol_references([
                SymbolReference(symbol_for_source_file.name,
                                path_or_string_reference_restrictions(PATH_RELATIVITY_VARIANTS_FOR_EXECUTABLE)),
                SymbolReference(argument_symbol.name,
                                no_restrictions()),
            ]),
        )
        check_execution(self,
                        sut.constructor(self.command_that_runs_python_file),
                        arrangement,
                        expectation)


PATH_RELATIVITY_VARIANTS_FOR_EXECUTABLE = PathRelativityVariants({RelOptionType.REL_HOME},
                                                                 absolute=True)
