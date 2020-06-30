import unittest
from pathlib import PurePosixPath

from exactly_lib.instructions.multi_phase import define_symbol as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.type_system.value_type import LogicValueType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources.embryo_checker import INSTRUCTION_CHECKER
from exactly_lib_test.instructions.multi_phase.define_symbol.test_resources.source_formatting import *
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.symbol.test_resources import sdv_type_assertions
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.container_assertions import matches_container_of_logic_type
from exactly_lib_test.symbol.test_resources.files_condition import FilesConditionSymbolContext
from exactly_lib_test.symbol.test_resources.symbol_syntax import NOT_A_VALID_SYMBOL_NAME
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_case_utils.files_condition.test_resources import arguments_building as arg_syntax
from exactly_lib_test.test_case_utils.files_condition.test_resources import primitive_assertions as asrt_primitive
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.quoting import surrounded_by_hard_quotes
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenarios),
        unittest.makeSuite(TestUnsuccessfulScenarios),
    ])


class TestSuccessfulScenarios(unittest.TestCase):
    def test_successful_parse_of_arbitrary_matcher(self):
        defined_name = 'defined_name'
        file_name = 'the-file-name'

        # ARRANGE #

        argument_cases = [
            NameAndValue('value on same line',
                         '{files_condition}'
                         ),
            NameAndValue('value on following line',
                         '{new_line} {files_condition}'
                         ),
        ]

        for case in argument_cases:
            with self.subTest(case.name):
                source = remaining_source(
                    src2(ValueType.FILES_CONDITION, defined_name, case.value,
                         files_condition=arg_syntax.FilesCondition([arg_syntax.FileCondition(file_name)])),
                )

                # EXPECTATION #

                expected_container = matches_container_of_logic_type(
                    LogicValueType.FILES_CONDITION,
                    sdv_type_assertions.matches_sdv_of_files_condition_constant(
                        primitive_value=asrt_primitive.files_matches({
                            PurePosixPath(file_name): asrt.is_none
                        })
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

                INSTRUCTION_CHECKER.check(self, source, ArrangementWithSds(), expectation)

    def test_successful_parse_of_reference(self):
        defined_name = 'defined_name'

        referenced_symbol = FilesConditionSymbolContext.of_arbitrary_value('referenced_name')

        # ARRANGE #

        source = remaining_source(
            src__const(ValueType.FILES_CONDITION, defined_name, referenced_symbol.name),
        )

        arrangement = ArrangementWithSds()

        # EXPECTATION #

        expected_container = matches_container_of_logic_type(
            LogicValueType.FILES_CONDITION,
            sdv_type_assertions.matches_sdv_of_files_condition_constant(
                references=asrt.matches_sequence([
                    referenced_symbol.reference_assertion
                ]),
                symbols=referenced_symbol.symbol_table)
        )

        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                asrt_sym_usage.matches_definition(asrt.equals(defined_name),
                                                  expected_container),
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                defined_name,
                expected_container,
            )
        )

        # ACT & ASSERT #

        INSTRUCTION_CHECKER.check(self, source, arrangement, expectation)


class TestUnsuccessfulScenarios(unittest.TestCase):
    def test_failing_parse(self):
        cases = [
            NameAndValue(
                'missing argument',
                '',
            ),
            NameAndValue(
                'single quoted argument',
                str(surrounded_by_hard_quotes(arg_syntax.FilesCondition.empty())),
            ),
            NameAndValue(
                'non-transformer name that is not a valid symbol name',
                NOT_A_VALID_SYMBOL_NAME,
            ),
        ]
        # ARRANGE #
        defined_name = 'defined_name'
        parser = sut.EmbryoParser()
        for case in cases:
            with self.subTest(case.name):
                source = remaining_source(
                    src__const(ValueType.FILES_CONDITION, defined_name, case.value),
                )
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    # ACT & ASSERT #
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())