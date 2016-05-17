from exactly_lib.section_document import model
from exactly_lib.section_document import parse
from exactly_lib.section_document import syntax
from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.act.phase_setup import PhaseEnvironmentForScriptGeneration
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util import line_source


class PlainSourceActPhaseParser(parse.SectionElementParser):
    def apply(self, source: line_source.LineSequenceBuilder) -> model.PhaseContentElement:
        while source.has_next():
            next_line = source.next_line()
            if syntax.is_section_header_line(next_line):
                source.return_line()
                break
        line_sequence = source.build()
        source_code = line_sequence.text
        return model.PhaseContentElement(model.ElementType.INSTRUCTION,
                                         line_sequence,
                                         SourceCodeInstruction(source_code))


class SourceCodeInstruction(ActPhaseInstruction):
    def __init__(self,
                 source_code: str):
        self.source_code = source_code

    def main(self, global_environment: common.GlobalEnvironmentForPostEdsPhase,
             script_generator: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        script_generator.append.raw_script_statement(self.source_code)
        return sh.new_sh_success()
