from shellcheck_lib.cli.instruction_setup import InstructionsSetup
from shellcheck_lib.execution import phases
from shellcheck_lib.document import model
from shellcheck_lib.document import parse
from shellcheck_lib.document.parse import InstructionParser, SourceError, ParserForPhase
from shellcheck_lib.general import line_source
from shellcheck_lib.general.line_source import LineSource
from shellcheck_lib.instructions.instruction_parser_for_single_phase import \
    InstructionParserForDictionaryOfInstructions
from shellcheck_lib.test_case import test_case_struct
from shellcheck_lib.test_case import instructions


class Parser:
    def __init__(self,
                 ptc_parser: parse.PlainTestCaseParser):
        self.__ptc_parser = ptc_parser

    def apply(self,
              plain_test_case: LineSource) -> test_case_struct.TestCase:
        document = self.__ptc_parser.apply(plain_test_case)
        return test_case_struct.TestCase(
            document.elements_for_phase_or_empty_if_phase_not_present(phases.ANONYMOUS.name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.SETUP.name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.ACT.name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.ASSERT.name),
            document.elements_for_phase_or_empty_if_phase_not_present(phases.CLEANUP.name),
        )


def new_parser(split_line_into_name_and_argument_function,
               instructions_setup: InstructionsSetup) -> Parser:
    def dict_parser(instruction_set: dict) -> InstructionParser:
        return InstructionParserForDictionaryOfInstructions(split_line_into_name_and_argument_function,
                                                            instruction_set)

    anonymous_phase = parse.ParserForPhase(phases.ANONYMOUS.name,
                                           dict_parser(instructions_setup.config_instruction_set))
    configuration = parse.PhaseAndInstructionsConfiguration(
        anonymous_phase,
        (
            ParserForPhase(phases.SETUP.name,
                           dict_parser(instructions_setup.setup_instruction_set)),
            ParserForPhase(phases.ACT.name,
                           PlainSourceActPhaseParser()),
            ParserForPhase(phases.ASSERT.name,
                           dict_parser(instructions_setup.assert_instruction_set)),
            ParserForPhase(phases.CLEANUP.name,
                           dict_parser(instructions_setup.cleanup_instruction_set)),
        )
    )
    return Parser(parse.new_parser_for(configuration))


class InstructionParserThatFailsUnconditionally(InstructionParser):
    def apply(self, line: line_source.Line) -> model.PhaseContentElement:
        raise SourceError(line, 'This parser fails unconditionally')


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