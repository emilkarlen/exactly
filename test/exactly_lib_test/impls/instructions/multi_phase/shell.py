import sys
import unittest

from exactly_lib.impls.instructions.multi_phase import shell as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.impls.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import Arrangement, Expectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants
from exactly_lib_test.impls.types.program.test_resources import result_assertions
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.section_document.test_resources.parse_source_assertions import assert_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.ds_construction import TcdsArrangement
from exactly_lib_test.tcfs.test_resources.tcds_populators import \
    TcdsPopulatorForRelOptionType
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSymbolReferences),
        unittest.makeSuite(TestFailingParse),
        suite_for_instruction_documentation(sut.DescriptionForNonAssertPhaseInstruction('instruction name',
                                                                                        'phase_name'))
    ])


class TestFailingParse(unittest.TestCase):
    def test_fail_when_only_white_space_on_line(self):
        parser = sut.embryo_parser('instruction-name')
        for source in equivalent_source_variants(self, '   '):
            with self.assertRaises(SingleInstructionInvalidArgumentException):
                parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestSymbolReferences(unittest.TestCase):
    def test_symbol_references(self):
        expected_exit_status = 72
        file_to_interpret = fs.File('python-logic_symbol_utils.py',
                                    py_script_that_exists_with_status(expected_exit_status))
        file_to_interpret_symbol = StringConstantSymbolContext('file_to_interpret_symbol',
                                                               file_to_interpret.file_name)
        python_interpreter_symbol = StringConstantSymbolContext('python_interpreter_symbol', sys.executable)

        argument = ' "{python_interpreter}" {file_to_interpret}'.format(
            python_interpreter=python_interpreter_symbol.name__sym_ref_syntax,
            file_to_interpret=file_to_interpret_symbol.name__sym_ref_syntax,
        )

        following_line = 'following line'
        source = remaining_source(argument, [following_line])

        arrangement = Arrangement.phase_agnostic(
            tcds=TcdsArrangement(
                tcds_contents=TcdsPopulatorForRelOptionType(
                    RelOptionType.REL_ACT,
                    fs.DirContents([file_to_interpret])),
            ),
            symbols=SymbolContext.symbol_table_of_contexts([
                python_interpreter_symbol,
                file_to_interpret_symbol,
            ]),
        )

        expectation = Expectation.phase_agnostic(
            source=assert_source(current_line_number=asrt.equals(2),
                                 column_index=asrt.equals(0)),
            symbol_usages=asrt.matches_sequence([
                python_interpreter_symbol.usage_assertion__w_str_rendering,
                file_to_interpret_symbol.usage_assertion__w_str_rendering,
            ]),
            main_result=result_assertions.equals(expected_exit_status, ''),
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
