from exactly_lib.section_document import model
from exactly_lib.section_document import parse
from exactly_lib.section_document import syntax
from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util import line_source
from exactly_lib.util.line_source import LineSequence


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


class SourceCodeInstruction(ActPhaseInstruction):
    def __init__(self,
                 source_code: LineSequence):
        self._source_code = source_code

    def source_code(self) -> LineSequence:
        return self._source_code

    def main(self, global_environment: common.GlobalEnvironmentForPostEdsPhase,
             script_generator: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        script_generator.append.raw_script_statement(self._source_code.text)
        return sh.new_sh_success()
