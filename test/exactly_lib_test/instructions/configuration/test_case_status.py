import unittest

from exactly_lib.definitions.instruction_arguments import ASSIGNMENT_OPERATOR
from exactly_lib.instructions.configuration import test_case_status as sut
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case import test_case_status as tcs
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.configuration.test_resources import configuration_builder_assertions as asrt_conf
from exactly_lib_test.instructions.configuration.test_resources.instruction_check import TestCaseBase, \
    Arrangement, Expectation
from exactly_lib_test.instructions.configuration.test_resources.source_with_assignment import syntax_for_assignment_of
from exactly_lib_test.section_document.test_resources.misc import ARBITRARY_FS_LOCATION_INFO
from exactly_lib_test.test_case.actor.test_resources.actors import actor_that_runs_constant_actions
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants, \
    equivalent_source_variants__with_source_check__consume_last_line
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestChangeStatus),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


class TestParse(unittest.TestCase):
    def test_invalid_syntax(self):
        cases = [
            '   ',
            ASSIGNMENT_OPERATOR + ' ',
            ' '.join([ASSIGNMENT_OPERATOR, tcs.NAME_SKIP, tcs.NAME_PASS]),
        ]
        for argument_str in cases:
            with self.subTest(argument_str):
                for source in equivalent_source_variants(self, argument_str):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        sut.Parser().parse(ARBITRARY_FS_LOCATION_INFO, source)


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             expected: tcs.TestCaseStatus,
             initial: tcs.TestCaseStatus,
             argument: str):
        for source in equivalent_source_variants__with_source_check__consume_last_line(self, argument):
            self._check(sut.Parser(),
                        source,
                        Arrangement(test_case_status=initial,
                                    actor=actor_that_runs_constant_actions()),
                        Expectation(configuration=asrt_conf.has(test_case_status=asrt.is_(expected))))


class TestChangeStatus(TestCaseBaseForParser):
    def test_PASS(self):
        self._run(expected=tcs.TestCaseStatus.PASS,
                  initial=tcs.TestCaseStatus.SKIP,
                  argument=syntax_for_assignment_of(tcs.NAME_PASS))

    def test_SKIP(self):
        self._run(expected=tcs.TestCaseStatus.SKIP,
                  initial=tcs.TestCaseStatus.PASS,
                  argument=syntax_for_assignment_of(tcs.NAME_SKIP))

    def test_FAIL(self):
        self._run(expected=tcs.TestCaseStatus.FAIL,
                  initial=tcs.TestCaseStatus.PASS,
                  argument=syntax_for_assignment_of(tcs.NAME_FAIL))


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
