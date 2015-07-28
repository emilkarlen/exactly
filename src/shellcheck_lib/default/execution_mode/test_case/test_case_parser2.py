from shellcheck_lib.default.execution_mode.test_case.instruction_setup2 import InstructionsSetup
from shellcheck_lib.execution import phases
from shellcheck_lib.document import model
from shellcheck_lib.document import parse2
from shellcheck_lib.document.parse import InstructionParser
from shellcheck_lib.general import line_source
from shellcheck_lib.general.line_source import LineSource
from shellcheck_lib.instructions.instruction_parser_for_single_phase2 import \
    SectionElementParserForDictionaryOfInstructions
from shellcheck_lib.test_case import test_case_doc
from shellcheck_lib.test_case import instructions


class Parser:
    def __init__(self,
                 plain_file_parser: parse2.PlainDocumentParser):
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
    def dict_parser(instruction_set: dict) -> parse2.SectionElementParser:
        return SectionElementParserForDictionaryOfInstructions(split_line_into_name_and_argument_function,
                                                               instruction_set)

    anonymous_phase = dict_parser(instructions_setup.config_instruction_set)
    configuration = parse2.SectionsConfiguration(
        anonymous_phase,
        (
            parse2.SectionConfiguration(phases.SETUP.name,
                                        dict_parser(instructions_setup.setup_instruction_set)),
            parse2.SectionConfiguration(phases.ACT.name,
                                        PlainSourceActPhaseParser()),
            parse2.SectionConfiguration(phases.ASSERT.name,
                                        dict_parser(instructions_setup.assert_instruction_set)),
            parse2.SectionConfiguration(phases.CLEANUP.name,
                                        dict_parser(instructions_setup.cleanup_instruction_set)),
        )
    )
    return Parser(parse2.new_parser_for(configuration))


class PlainSourceActPhaseParser(InstructionParser):
    def apply(self, line: line_source.Line) -> model.PhaseContentElement:
        return model.new_instruction_element(line,
                                             SourceCodeInstruction(line.text))


class SourceCodeInstruction(instructions.ActPhaseInstruction):
    def __init__(self,
                 source_code: str):
        self.source_code = source_code

    def validate(self, global_environment: instructions.GlobalEnvironmentForPostEdsPhase) \
            -> instructions.SuccessOrValidationErrorOrHardError:
        return instructions.new_svh_success()

    def main(self, global_environment: instructions.GlobalEnvironmentForPostEdsPhase,
             script_generator: instructions.PhaseEnvironmentForScriptGeneration) -> instructions.SuccessOrHardError:
        script_generator.append.raw_script_statement(self.source_code)
        return instructions.new_sh_success()
