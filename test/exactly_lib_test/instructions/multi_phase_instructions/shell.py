import sys
import unittest

from exactly_lib.instructions.multi_phase_instructions import shell as sut
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.instructions.test_resources.assertion_utils import sub_process_result_check as spr_check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.data.restrictions.test_resources.concrete_restriction_assertion import \
    equals_data_type_reference_restrictions
from exactly_lib_test.symbol.data.test_resources import data_symbol_utils as su
from exactly_lib_test.symbol.test_resources.resolver_structure_assertions import matches_reference_2
from exactly_lib_test.test_case_file_structure.test_resources.home_and_sds_check.home_and_sds_populators import \
    HomeOrSdsPopulatorForRelOptionType
from exactly_lib_test.test_resources import file_structure as fs
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSymbolReferences),
        suite_for_instruction_documentation(sut.DescriptionForNonAssertPhaseInstruction('instruction name'))
    ])


class TestSymbolReferences(unittest.TestCase):
    def test_symbol_references(self):
        expected_exit_status = 72
        file_to_interpret = fs.File('python-program.py',
                                    py_script_that_exists_with_status(expected_exit_status))
        file_to_interpret_symbol = NameAndValue('file_to_interpret_symbol',
                                                file_to_interpret.file_name)
        python_interpreter_symbol = NameAndValue('python_interpreter_symbol', sys.executable)

        argument = ' "{python_interpreter}" {file_to_interpret}'.format(
            python_interpreter=symbol_reference_syntax_for_name(python_interpreter_symbol.name),
            file_to_interpret=symbol_reference_syntax_for_name(file_to_interpret_symbol.name),
        )

        following_line = 'following line'
        source = remaining_source(argument, [following_line])

        arrangement = ArrangementWithSds(
            home_or_sds_contents=HomeOrSdsPopulatorForRelOptionType(
                RelOptionType.REL_ACT,
                fs.DirContents([file_to_interpret])),
            symbols=SymbolTable({
                python_interpreter_symbol.name: su.string_constant_container(python_interpreter_symbol.value),
                file_to_interpret_symbol.name: su.string_constant_container(file_to_interpret_symbol.value),
            }),
        )

        expectation = embryo_check.Expectation(
            source=assert_source(current_line_number=asrt.equals(2),
                                 column_index=asrt.equals(0)),
            symbol_usages=asrt.matches_sequence([
                matches_reference_2(
                    python_interpreter_symbol.name,
                    equals_data_type_reference_restrictions(is_any_data_type())),
                matches_reference_2(
                    file_to_interpret_symbol.name,
                    equals_data_type_reference_restrictions(is_any_data_type())),
            ]),
            main_result=spr_check.is_success_result(expected_exit_status, ''),
        )

        parser = sut.embryo_parser('instruction-name')
        embryo_check.check(self, parser, source, arrangement, expectation)


def py_script_that_exists_with_status(status: int) -> str:
    return """
import sys
sys.exit({})
""".format(str(status))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
