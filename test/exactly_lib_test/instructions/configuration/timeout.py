import unittest

from exactly_lib.instructions.configuration import timeout as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.configuration.test_resources import configuration_builder_assertions as asrt_conf
from exactly_lib_test.instructions.configuration.test_resources.instruction_check import TestCaseBase, \
    Arrangement, Expectation
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_case.actor.test_resources.actors import actor_that_runs_constant_actions
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants, \
    equivalent_source_variants__with_source_check__consume_last_line
from exactly_lib_test.test_resources.test_utils import NIE
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestFailingParse(),
        TestSetTimeout(),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestFailingParse(unittest.TestCase):
    def runTest(self):
        cases = [
            '   ',
            'arg1 arg2',
            '= arg1 arg2',
            '= notAnInteger',
            '= -1',
            '= 1-2',
            '= "2"',
            '=5',
            '= 5/2',
            '= "hello"',
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
        for source in equivalent_source_variants__with_source_check__consume_last_line(self, argument):
            self._check(sut.Parser(),
                        source,
                        Arrangement(
                            actor=actor_that_runs_constant_actions(),
                            timeout_in_seconds=None),
                        Expectation(
                            configuration=asrt_conf.has(asrt.equals(expected))))


class TestSetTimeout(TestCaseBaseForParser):
    def runTest(self):
        cases = [
            NIE('constant 5',
                5,
                '5',
                ),
            NIE('constant 75',
                75,
                '75',
                ),
            NIE('python expr',
                5,
                '2+3',
                ),
            NIE('python expr with space',
                7,
                '2*3 + 1',
                ),
            NIE('python expr len',
                11,
                'len("hello world")',
                ),
        ]
        for case in cases:
            with self.subTest(case.name):
                self._run(
                    expected=case.expected_value,
                    argument='= ' + case.input_value
                )


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
