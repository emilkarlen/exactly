from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, SingleInstructionParserSource
from exactly_lib_test.instructions.assert_.test_resources import instruction_check


class TestConfiguration:
    def new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def source_for(self, argument_tail: str) -> SingleInstructionParserSource:
        raise NotImplementedError()

    def arrangement_for_contents(self, actual_contents: str) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()

    def arrangement_for_contents_from_fun(self, home_and_sds_2_str) -> instruction_check.ArrangementPostAct:
        raise NotImplementedError()
