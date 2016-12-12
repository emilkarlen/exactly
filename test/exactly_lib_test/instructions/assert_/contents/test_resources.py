from exactly_lib.instructions.assert_ import contents as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct


class TestCaseBaseForParser(instruction_check.TestCaseBase):
    def _run(self,
             source: SingleInstructionParserSource,
             arrangement: ArrangementPostAct,
             expectation: Expectation):
        self._check(sut.Parser(), source, arrangement, expectation)
