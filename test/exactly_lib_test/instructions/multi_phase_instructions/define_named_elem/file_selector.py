import unittest

from exactly_lib.instructions.multi_phase_instructions import assign_symbol as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.file_selectors.file_selectors import FileSelectorFromSelectors
from exactly_lib.test_case_utils.file_selectors.parse_file_selector import NAME_SELECTOR_NAME
from exactly_lib.util.dir_contents_selection import Selectors, all_files
from exactly_lib_test.instructions.multi_phase_instructions.define_named_elem.test_resources import *
from exactly_lib_test.instructions.multi_phase_instructions.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.multi_phase_instructions.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.named_element.test_resources import resolver_structure_assertions as asrt_ne
from exactly_lib_test.named_element.test_resources.resolver_structure_assertions import matches_container
from exactly_lib_test.named_element.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_case_utils.file_selectors.test_resources.resolver_assertions import \
    resolved_value_equals_file_selector
from exactly_lib_test.test_case_utils.parse.test_resources.selection_arguments import selectors_arguments
from exactly_lib_test.test_resources.parse import single_line_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestSuccessfulScenarios)


class TestCaseBase(unittest.TestCase):
    def _check(self,
               source: ParseSource,
               arrangement: ArrangementWithSds,
               expectation: Expectation,
               ):
        parser = sut.EmbryoParser()
        embryo_check.check(self, parser, source, arrangement, expectation)


class TestSuccessfulScenarios(TestCaseBase):
    def test_successful_parse(self):
        name_pattern = 'the name pattern'
        cases = [
            ('empty RHS SHOULD give selection of all files',
             '',
             all_files(),
             ),
            ('name pattern in RHS SHOULD give selection of name pattern',
             selectors_arguments(name_pattern=name_pattern),
             Selectors(name_patterns=frozenset([name_pattern])),
             ),
            ('file type in RHS SHOULD give selection of name pattern',
             selectors_arguments(type_selection=FileType.REGULAR),
             Selectors(file_types=frozenset([FileType.REGULAR])),
             ),
        ]
        # ARRANGE #
        defined_name = 'defined_name'
        for name, rhs_source, expected_selectors in cases:
            with self.subTest(name=name):
                source = single_line_source(
                    src('{file_sel_type} {defined_name} = {selector_argument}',
                        defined_name=defined_name,
                        selector_argument=rhs_source),
                )

                expected_container = matches_container(
                    resolved_value_equals_file_selector(FileSelectorFromSelectors(expected_selectors))
                )

                expectation = Expectation(
                    symbol_usages=asrt.matches_sequence([
                        asrt_ne.matches_definition(asrt.equals(defined_name),
                                                   expected_container)
                    ]),
                    symbols_after_main=assert_symbol_table_is_singleton(
                        defined_name,
                        expected_container,
                    )
                )
                # ACT & ASSERT #
                self._check(source, ArrangementWithSds(), expectation)

    def test_failing_parse(self):
        cases = [
            (
                'single quoted argument',
                str(surrounded_by_hard_quotes(NAME_SELECTOR_NAME)),
            ),
            (
                'non-selector name that is not a valid symbol name',
                NOT_A_VALID_SYMBOL_NAME,
            ),
        ]
        # ARRANGE #
        defined_name = 'defined_name'
        parser = sut.EmbryoParser()
        for name, rhs_source in cases:
            with self.subTest(name=name):
                source = single_line_source(
                    src('{file_sel_type} {defined_name} = {selector_argument}',
                        defined_name=defined_name,
                        selector_argument=rhs_source),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT & ASSERT #
                    parser.parse(source)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
