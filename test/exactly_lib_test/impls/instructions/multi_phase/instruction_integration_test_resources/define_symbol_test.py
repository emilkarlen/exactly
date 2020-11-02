import unittest

from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.value_type import ValueType
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.common_failing_cases import \
    INVALID_SYNTAX_CASES
from exactly_lib_test.impls.instructions.multi_phase.define_symbol.test_resources.source_formatting import src2
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.section_document.test_resources.parse_source import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    test_cases = [
        TestFailWhenInvalidSyntax,
        TestSuccessfulDefinition,
    ]
    suites = []
    for test_case in test_cases:
        suites.append(test_case(conf))
    suites.append(suite_for_instruction_documentation(conf.documentation()))
    return unittest.TestSuite(suites)


class TestCaseBase(unittest.TestCase):
    def __init__(self, conf: ConfigurationBase):
        super().__init__()
        self.conf = conf

    def shortDescription(self):
        return '{}\n / {}'.format(type(self),
                                  type(self.conf))


class TestFailWhenInvalidSyntax(TestCaseBase):
    def runTest(self):
        parser = self.conf.parser()
        for (source_str, case_name) in INVALID_SYNTAX_CASES:
            source = remaining_source(source_str)
            with self.subTest(msg=case_name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    parser.parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestSuccessfulDefinition(TestCaseBase):
    def runTest(self):
        source = src2(ValueType.STRING, 'name', 'value')
        expected_symbol = StringConstantSymbolContext('name', 'value')

        self.conf.run_single_line_test_with_source_variants_and_source_check(
            self,
            source,
            self.conf.arrangement(),
            self.conf.expect_success(
                symbol_usages=asrt.matches_sequence([
                    expected_symbol.assert_matches_definition_of_sdv
                ])
            )
        )
