import unittest

from exactly_lib.definitions.primitives.file_matcher import NAME_MATCHER_NAME
from exactly_lib.instructions.multi_phase import define_symbol as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources import *
from exactly_lib_test.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import single_line_source
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.sdv_structure_assertions import matches_container
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_utils.file_matcher.test_resources import ddv_assertions as asrt_file_matcher
from exactly_lib_test.test_case_utils.file_matcher.test_resources.argument_syntax import file_matcher_arguments
from exactly_lib_test.test_case_utils.file_matcher.test_resources.sdv_assertions import \
    resolved_ddv_matches_file_matcher
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.test_resources import file_matcher
from exactly_lib_test.type_system.logic.test_resources import matcher_assertions as asrt_matcher
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
            NIE('empty RHS SHOULD give selection of all files',
                asrt_matcher.is_equivalent_to(
                    constant.MatcherWithConstantResult(True),
                    [asrt_matcher.ModelInfo(file_matcher.FileMatcherModelThatMustNotBeAccessed())]
                ),
                '',
                ),
            NIE('name pattern in RHS SHOULD give selection of name pattern',
                asrt_file_matcher.is_name_glob_pattern(asrt.equals(name_pattern)),
                file_matcher_arguments(name_pattern=name_pattern),
                ),
            NIE('file type in RHS SHOULD give selection of name pattern',
                asrt_file_matcher.is_type_matcher(FileType.REGULAR),
                file_matcher_arguments(type_match=FileType.REGULAR),
                ),
        ]
        # ARRANGE #
        defined_name = 'defined_name'
        for case in cases:
            with self.subTest(case.name):
                source = single_line_source(
                    src('{file_matcher_type} {defined_name} = {selector_argument}',
                        defined_name=defined_name,
                        selector_argument=case.input_value),
                )

                expected_container = matches_container(
                    resolved_ddv_matches_file_matcher(
                        asrt_file_matcher.matches_file_matcher_ddv__deep(
                            case.expected_value
                        )
                    )
                )

                expectation = Expectation(
                    symbol_usages=asrt.matches_sequence([
                        asrt_sym_usage.matches_definition(asrt.equals(defined_name),
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
                str(surrounded_by_hard_quotes(NAME_MATCHER_NAME)),
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
                    src('{file_matcher_type} {defined_name} = {selector_argument}',
                        defined_name=defined_name,
                        selector_argument=rhs_source),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT & ASSERT #
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
