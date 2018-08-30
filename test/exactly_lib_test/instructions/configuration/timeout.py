import unittest

from exactly_lib.instructions.configuration import timeout as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.configuration.test_resources import configuration_builder_assertions as asrt_conf
from exactly_lib_test.instructions.configuration.test_resources.instruction_check import TestCaseBase, \
    Arrangement, Expectation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants, \
    equivalent_source_variants__with_source_check
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_case.act_phase_handling.test_resources.act_phase_handlings import \
    act_phase_handling_that_runs_constant_actions
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestFailingParse),
        unittest.makeSuite(TestSetTimeout),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestFailingParse(unittest.TestCase):
    def test(self):
        cases = [
            '   ',
            'arg1 arg2',
            'notAnInteger',
            '-1',
            '=5',
        ]
        for argument_str in cases:
            with self.subTest(argument_str):
                for source in equivalent_source_variants(self, argument_str):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.Parser().parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             expected: int,
             argument: str):
        for source in equivalent_source_variants__with_source_check(self, argument):
            self._check(sut.Parser(),
                        source,
                        Arrangement(
                            act_phase_handling=act_phase_handling_that_runs_constant_actions(),
                            timeout_in_seconds=None),
                        Expectation(
                            configuration=asrt_conf.has(asrt.equals(expected))))


class TestSetTimeout(TestCaseBaseForParser):
    def test_5(self):
        self._run(expected=5,
                  argument='= 5')

    def test_75(self):
        self._run(expected=75,
                  argument='  = 75')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
