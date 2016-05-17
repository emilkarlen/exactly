from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SectionElementParserForStandardCommentAndEmptyLines
from exactly_lib.test_case.phases import common
from exactly_lib.test_case.phases.act.instruction import ActPhaseInstruction
from exactly_lib.test_case.phases.act.phase_setup import PhaseEnvironmentForScriptGeneration
from exactly_lib.test_case.phases.result import sh
from exactly_lib.util import line_source


class PlainSourceActPhaseParser(SectionElementParserForStandardCommentAndEmptyLines):
    def _parse_instruction(self, source: line_source.LineSequenceBuilder) -> ActPhaseInstruction:
        return SourceCodeInstruction(source.first_line.text)


class SourceCodeInstruction(ActPhaseInstruction):
    def __init__(self,
                 source_code: str):
        self.source_code = source_code

    def main(self, global_environment: common.GlobalEnvironmentForPostEdsPhase,
             script_generator: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        script_generator.append.raw_script_statement(self.source_code)
        return sh.new_sh_success()
