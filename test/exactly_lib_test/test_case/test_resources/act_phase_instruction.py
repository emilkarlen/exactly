from exactly_lib.processing.parse.act_phase_source_parser import SourceCodeInstruction
from exactly_lib.util.line_source import LineSequence


def instr(lines: list,
          first_line_number: int = 1) -> SourceCodeInstruction:
    return SourceCodeInstruction(LineSequence(first_line_number,
                                              tuple(lines)))
