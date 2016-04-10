from shellcheck_lib.document import parse
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SectionElementParserForDictionaryOfInstructions, SectionElementParserForStandardCommentAndEmptyLines
from shellcheck_lib.execution import phases
from shellcheck_lib.test_case import test_case_doc
from shellcheck_lib.test_case.instruction_setup import InstructionsSetup
from shellcheck_lib.test_case.phases import common
from shellcheck_lib.test_case.phases.act.instruction import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.util import line_source

DEFAULT_PHASE = phases.ACT


class Parser:
    def __init__(self,
                 plain_file_parser: parse.PlainDocumentParser):
        self.__plain_file_parser = plain_file_parser

    def apply(self,
              plain_test_case: line_source.LineSource) -> test_case_doc.TestCase:
        document = self.__plain_file_parser.apply(plain_test_case)
        return test_case_doc.TestCase(
            document.elements_for_phase_or_empty_if_phase_not_present(phases.ANONYMOUS.section_name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.SETUP.section_name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.ACT.section_name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.BEFORE_ASSERT.section_name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.ASSERT.section_name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.CLEANUP.section_name),
        )


def new_parser(split_line_into_name_and_argument_function,
               act_phase_parser: parse.SectionElementParser,
               instructions_setup: InstructionsSetup) -> Parser:
    def dict_parser(instruction_set: dict) -> parse.SectionElementParser:
        return SectionElementParserForDictionaryOfInstructions(split_line_into_name_and_argument_function,
                                                               instruction_set)

    configuration = parse.SectionsConfiguration(
        (
            parse.SectionConfiguration(phases.ANONYMOUS.section_name,
                                       dict_parser(instructions_setup.config_instruction_set)),
            parse.SectionConfiguration(phases.SETUP.section_name,
                                       dict_parser(instructions_setup.setup_instruction_set)),
            parse.SectionConfiguration(phases.ACT.section_name,
                                       act_phase_parser),
            parse.SectionConfiguration(phases.BEFORE_ASSERT.section_name,
                                       dict_parser(instructions_setup.before_assert_instruction_set)),
            parse.SectionConfiguration(phases.ASSERT.section_name,
                                       dict_parser(instructions_setup.assert_instruction_set)),
            parse.SectionConfiguration(phases.CLEANUP.section_name,
                                       dict_parser(instructions_setup.cleanup_instruction_set)),
        ),
        default_phase_name=DEFAULT_PHASE.section_name
    )
    return Parser(parse.new_parser_for(configuration))


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
