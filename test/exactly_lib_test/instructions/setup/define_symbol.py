import unittest

from exactly_lib.help_texts.file_ref import REL_ACT_OPTION
from exactly_lib.instructions.setup import define_symbol as sut
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib_test.common.help.test_resources.check_documentation import suite_for_instruction_documentation
from exactly_lib_test.instructions.multi_phase_instructions.define_symbol.test_resources import *
from exactly_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestPathSuccessfulParse),
        suite_for_instruction_documentation(sut.setup('instruction name').documentation),
    ])


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: ParseSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.setup('instr-name'), source, arrangement, expectation)


class TestPathSuccessfulParse(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        setup = sut.setup('instruction-name')
        source = single_line_source('{path_type} name = {rel_opt} component',
                                    rel_opt=REL_ACT_OPTION)
        # ACT #
        instruction = setup.parse(source)
        # ASSERT #
        self.assertIsInstance(instruction, SetupPhaseInstruction,
                              'Instruction must be an ' + str(SetupPhaseInstruction))
