from shellcheck_lib.document import model
from shellcheck_lib.document import parse
from shellcheck_lib.general import line_source
from shellcheck_lib.test_suite import instruction
from shellcheck_lib.test_suite import test_suite_struct

SECTION_NAME__SUITS = 'testsuits'
SECTION_NAME__CASES = 'testcases'


class TestSuiteFileInstruction(instruction.TestSuiteSectionInstruction):
    def __init__(self, file_name: str):
        self._file_name = file_name

    def resolve_paths(self, environment: instruction.Environment) -> list:
        """
        :raises FileNotAccessibleError: A referenced file is not accessible.
        :return: [pathlib.Path]
        """
        raise NotImplementedError()


class TestCaseFileInstruction(instruction.TestCaseSectionInstruction):
    def __init__(self, file_name: str):
        self._file_name = file_name

    def resolve_paths(self, environment: instruction.Environment) -> list:
        raise NotImplementedError("case file instr")


class SuitesSectionParser(parse.InstructionParser):
    def apply(self, source_line: line_source.Line) -> model.PhaseContentElement:
        return model.new_instruction_element(source_line,
                                             TestSuiteFileInstruction(source_line.text))


class CasesSectionParser(parse.InstructionParser):
    def apply(self, source_line: line_source.Line) -> model.PhaseContentElement:
        return model.new_instruction_element(source_line,
                                             TestCaseFileInstruction(source_line.text))


PARSER_CONFIGURATION = parse.PhaseAndInstructionsConfiguration(
    None,
    (parse.ParserForPhase(SECTION_NAME__SUITS, SuitesSectionParser()),
     parse.ParserForPhase(SECTION_NAME__CASES, CasesSectionParser()),
     )
)


class Parser:
    def __init__(self):
        self.__plain_file_parser = parse.new_parser_for(PARSER_CONFIGURATION)

    def apply(self,
              plain_test_case: line_source.LineSource) -> test_suite_struct.TestSuite:
        document = self.__plain_file_parser.apply(plain_test_case)
        return test_suite_struct.TestSuite(
            document.elements_for_phase_or_empty_if_phase_not_present(SECTION_NAME__SUITS),
            document.elements_for_phase_or_empty_if_phase_not_present(SECTION_NAME__CASES),
        )


PARSER = Parser()
