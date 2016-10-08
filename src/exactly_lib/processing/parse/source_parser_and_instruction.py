from exactly_lib.section_document import model
from exactly_lib.section_document import parse
from exactly_lib.section_document import syntax
from exactly_lib.test_case.phases.act.instruction import SourceCodeInstruction
from exactly_lib.util import line_source


class PlainSourceActPhaseParser(parse.SectionElementParser):
    def apply(self, source: line_source.LineSequenceBuilder) -> model.SectionContentElement:
        while source.has_next():
            next_line = source.next_line()
            if syntax.is_section_header_line(next_line):
                source.return_line()
                break
        line_sequence = source.build()
        return model.SectionContentElement(model.ElementType.INSTRUCTION,
                                           line_sequence,
                                           SourceCodeInstruction(line_sequence))

