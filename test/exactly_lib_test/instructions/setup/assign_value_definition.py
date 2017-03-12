import unittest

from exactly_lib.instructions.setup import assign_value_definition as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case import file_refs
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.test_case.value_definition import ValueDefinitionOfPath
from exactly_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_case.test_resources import value_definition as tr
from exactly_lib_test.test_resources.parse import remaining_source


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingParse))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulParse))
    ret_val.addTest(unittest.makeSuite(TestAssignmentRelativeSingleValidOption))
    return ret_val


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: ParseSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.Parser(), source, arrangement, expectation)


class TestFailingParse(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('', 'Empty source'),
            ('val_name', 'Only VAL-NAME'),
            ('val_name --rel-home x', 'Missing ='),
            ('"val_name" = --rel-act x', 'VAL-NAME must not be quoted'),
            ('name = --rel-act x superfluous-arg', 'Superfluous arguments'),
            ('name SuperfluousName = --rel-act x', 'Superfluous name'),
        ]
        setup = sut.setup('instruction-name')
        for (source_str, case_name) in test_cases:
            source = remaining_source(source_str)
            with self.subTest(msg=case_name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    setup.parse(source)


class TestSuccessfulParse(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        setup = sut.setup('instruction-name')
        source = remaining_source('name = --rel-act component')
        # ACT #
        instruction = setup.parse(source)
        # ASSERT #
        self.assertIsInstance(instruction, SetupPhaseInstruction,
                              'Instruction must be an ' + str(SetupPhaseInstruction))


class TestAssignmentRelativeSingleValidOption(TestCaseBaseForParser):
    def test(self):
        instruction_argument = 'name = --rel-act component'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            self._run(source,
                      Arrangement(),
                      Expectation(
                          value_definition_usages=tr.assert_value_usages_is_singleton_list(
                              tr.equals_value_definition(
                                  ValueDefinitionOfPath('name',
                                                        tr.file_ref_value(file_refs.rel_act('component'))))))
                      )
