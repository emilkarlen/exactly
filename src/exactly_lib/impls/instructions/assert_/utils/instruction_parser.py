from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, \
    TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction


class AssertPhaseInstructionParser(InstructionParserWithoutSourceFileLocationInfo):
    def parse_from_source(self, source: ParseSource) -> AssertPhaseInstruction:
        raise NotImplementedError('abstract method')


class AssertPhaseInstructionTokenParser(AssertPhaseInstructionParser):
    def parse_from_source(self, source: ParseSource) -> AssertPhaseInstruction:
        with from_parse_source(source,
                               consume_last_line_if_is_at_eol_after_parse=True) as parser:
            return self.parse_from_token_parser(parser)

    def parse_from_token_parser(self, parser: TokenParser) -> AssertPhaseInstruction:
        raise NotImplementedError('abstract method')
