from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct


class TestWithParserBase(instruction_check.TestCaseBase):
    def _new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def _run(self,
             source: SingleInstructionParserSource,
             arrangement: ArrangementPostAct,
             expectation: Expectation):
        self._check(self._new_parser(), source, arrangement, expectation)
