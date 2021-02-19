import pathlib
import unittest

from exactly_lib.definitions.primitives.file_matcher import NAME_MATCHER_NAME
from exactly_lib.impls.instructions.multi_phase.define_symbol import parser as sut
from exactly_lib.impls.types.file_matcher import parse_file_matcher, file_matcher_models
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.value_type import LogicValueType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources import matcher_helpers
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.embryo_checker import \
    INSTRUCTION_CHECKER
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.source_formatting import *
from exactly_lib_test.impls.instructions.multi_phase.test_resources.embryo_arr_exp import Arrangement, Expectation
from exactly_lib_test.impls.types.file_matcher.test_resources.argument_syntax import file_matcher_arguments
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import single_line_source
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.dep_variants.test_resources import type_sdv_assertions
from exactly_lib_test.type_val_deps.dep_variants.test_resources.resolving_helper import resolving_helper__fake
from exactly_lib_test.type_val_deps.sym_ref.test_resources.container_assertions import matches_container_of_logic_type
from exactly_lib_test.type_val_deps.types.path.test_resources import described_path
from exactly_lib_test.type_val_deps.types.test_resources.file_matcher import FileMatcherSymbolContext
from exactly_lib_test.type_val_prims.matcher.test_resources import matcher_assertions as asrt_matcher
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def test_successful_parse(self):
        name_pattern = 'the name pattern'
        non_matching_name = 'non-matching name'

        glob_pattern_arguments = file_matcher_arguments(name_pattern=name_pattern)
        sut_parser = parse_file_matcher.parsers().full
        expected_glob_pattern_matcher_sdv = sut_parser.parse(remaining_source(glob_pattern_arguments))

        expected_glob_pattern_matcher = resolving_helper__fake().resolve_matcher(expected_glob_pattern_matcher_sdv)

        cases = [
            NIE('name pattern in RHS SHOULD give selection of name pattern',
                asrt_matcher.is_equivalent_to(
                    expected_glob_pattern_matcher,
                    [
                        asrt_matcher.ModelInfo(
                            file_matcher_models.FileMatcherModelForDescribedPath(
                                described_path.new_primitive(pathlib.Path(name_pattern)),
                            )),
                        asrt_matcher.ModelInfo(
                            file_matcher_models.FileMatcherModelForDescribedPath(
                                described_path.new_primitive(pathlib.Path(non_matching_name)),
                            )),
                    ]
                ),
                glob_pattern_arguments,
                ),
        ]
        # ARRANGE #
        defined_name = 'defined_name'
        argument_cases = [
            NameAndValue('value on same line',
                         '{selector_argument}'
                         ),
            NameAndValue('value on following line',
                         '{new_line} {selector_argument}'
                         ),
        ]

        for case in cases:
            for argument_case in argument_cases:
                with self.subTest(case.name,
                                  arguments=argument_case.name):
                    source = single_line_source(
                        src2(ValueType.FILE_MATCHER, defined_name, argument_case.value,
                             selector_argument=case.input_value),
                    )

                    expected_container = matches_container_of_logic_type(
                        LogicValueType.FILE_MATCHER,
                        type_sdv_assertions.matches_sdv_of_file_matcher(
                            references=asrt.is_empty_sequence,
                            primitive_value=case.expected_value
                        )
                    )

                    expectation = Expectation.phase_agnostic(
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
                    INSTRUCTION_CHECKER.check(self, source, Arrangement.phase_agnostic(), expectation)

    def test_matcher_SHOULD_be_parsed_as_full_expression(self):
        matcher_helpers.check_matcher_should_be_parsed_as_full_expression(
            self,
            FileMatcherSymbolContext.of_arbitrary_value('symbol_1'),
            FileMatcherSymbolContext.of_arbitrary_value('symbol_2'),
            LogicValueType.FILE_MATCHER,
        )

    def test_failing_parse(self):
        cases = [
            NameAndValue(
                'single quoted argument',
                str(surrounded_by_hard_quotes(NAME_MATCHER_NAME)),
            ),
            NameAndValue(
                'non-selector name that is not a valid symbol name',
                NOT_A_VALID_SYMBOL_NAME,
            ),
            NameAndValue(
                'missing matcher',
                '',
            ),
        ]
        # ARRANGE #
        defined_name = 'defined_name'
        parser = sut.EmbryoParser()
        for case in cases:
            with self.subTest(name=case.name):
                source = single_line_source(
                    src2(ValueType.FILE_MATCHER, defined_name, case.value),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT & ASSERT #
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
