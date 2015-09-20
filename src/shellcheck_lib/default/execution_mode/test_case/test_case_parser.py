from shellcheck_lib.default.execution_mode.test_case.instruction_setup import InstructionsSetup
from shellcheck_lib.document.model import Instruction
from shellcheck_lib.execution import phases
from shellcheck_lib.document import parse
from shellcheck_lib.general import line_source
from shellcheck_lib.general.line_source import LineSource
from shellcheck_lib.instructions.instruction_parser_for_single_phase import \
    SectionElementParserForDictionaryOfInstructions, SectionElementParserForStandardCommentAndEmptyLines
from shellcheck_lib.test_case import test_case_doc
from shellcheck_lib.test_case.instruction import common
from shellcheck_lib.test_case.instruction.result import sh
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.instruction.sections.act import ActPhaseInstruction, PhaseEnvironmentForScriptGeneration


class Parser:
    def __init__(self,
                 plain_file_parser: parse.PlainDocumentParser):
        self.__plain_file_parser = plain_file_parser

    def apply(self,
              plain_test_case: LineSource) -> test_case_doc.TestCase:
        document = self.__plain_file_parser.apply(plain_test_case)
        return test_case_doc.TestCase(
            document.elements_for_phase_or_empty_if_phase_not_present(phases.ANONYMOUS.name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.SETUP.name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.ACT.name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.ASSERT.name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.CLEANUP.name),
        )


def new_parser(split_line_into_name_and_argument_function,
               instructions_setup: InstructionsSetup) -> Parser:
    def dict_parser(instruction_set: dict) -> parse.SectionElementParser:
        return SectionElementParserForDictionaryOfInstructions(split_line_into_name_and_argument_function,
                                                               instruction_set)

    anonymous_phase = dict_parser(instructions_setup.config_instruction_set)
    configuration = parse.SectionsConfiguration(
        anonymous_phase,
        (
            parse.SectionConfiguration(phases.SETUP.name,
                                        dict_parser(instructions_setup.setup_instruction_set)),
            parse.SectionConfiguration(phases.ACT.name,
                                        PlainSourceActPhaseParser()),
            parse.SectionConfiguration(phases.ASSERT.name,
                                        dict_parser(instructions_setup.assert_instruction_set)),
            parse.SectionConfiguration(phases.CLEANUP.name,
                                        dict_parser(instructions_setup.cleanup_instruction_set)),
        )
    )
    return Parser(parse.new_parser_for(configuration))


class PlainSourceActPhaseParser(SectionElementParserForStandardCommentAndEmptyLines):
    def _parse_instruction(self, source: line_source.LineSequenceBuilder) -> Instruction:
        return SourceCodeInstruction(source.first_line.text)


class SourceCodeInstruction(ActPhaseInstruction):
    def __init__(self,
                 source_code: str):
        self.source_code = source_code

    def validate(self, global_environment: common.GlobalEnvironmentForPostEdsPhase) \
            -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self, global_environment: common.GlobalEnvironmentForPostEdsPhase,
             script_generator: PhaseEnvironmentForScriptGeneration) -> sh.SuccessOrHardError:
        script_generator.append.raw_script_statement(self.source_code)
        return sh.new_sh_success()
