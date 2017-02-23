from exactly_lib.section_document.new_parser_classes import SectionElementParser
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.section_document.parser_implementations.new_section_element_parser import \
    InstructionWithoutDescriptionParser, StandardSyntaxElementParser
from exactly_lib.test_suite.instruction_set import instruction, utils
from exactly_lib.test_suite.instruction_set.instruction import Environment, TestSuiteInstruction


def new_parser() -> SectionElementParser:
    return StandardSyntaxElementParser(InstructionWithoutDescriptionParser(_CasesSectionParser()))


class TestCaseSectionInstruction(TestSuiteInstruction):
    def resolve_paths(self,
                      environment: Environment) -> list:
        """
        :raises FileNotAccessibleError: A referenced file is not accessible.
        :return: [pathlib.Path]
        """
        raise NotImplementedError()


class _CasesSectionParser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> TestCaseSectionInstruction:
        line_text = rest_of_line.strip()
        return _TestCaseWildcardFileInstruction(line_text) \
            if utils.is_wildcard_pattern(line_text) \
            else _TestCaseNonWildcardFileInstruction(line_text)


class _TestCaseNonWildcardFileInstruction(TestCaseSectionInstruction):
    """
    Resolves a single path from a file-name that does not contain wild-cards.
    """

    def __init__(self, file_name: str):
        self._file_name = file_name

    def resolve_paths(self, environment: instruction.Environment) -> list:
        return utils.resolve_non_wildcard_path(self._file_name, environment)


class _TestCaseWildcardFileInstruction(TestCaseSectionInstruction):
    """
    Resolves a list of paths from a file-name pattern.
    """

    def __init__(self, pattern: str):
        self._pattern = pattern

    def resolve_paths(self, environment: instruction.Environment) -> list:
        return utils.resolve_wildcard_paths(self._pattern, environment)
