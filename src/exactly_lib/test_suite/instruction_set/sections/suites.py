from exactly_lib.section_document.new_parser_classes import SectionElementParser
from exactly_lib.section_document.parser_implementations.instruction_parsers import \
    InstructionParserThatConsumesCurrentLine
from exactly_lib.section_document.parser_implementations.section_element_parsers import \
    StandardSyntaxElementParser, InstructionWithoutDescriptionParser
from exactly_lib.test_suite.instruction_set import instruction, utils
from exactly_lib.test_suite.instruction_set.instruction import Environment, TestSuiteInstruction


def new_parser() -> SectionElementParser:
    return StandardSyntaxElementParser(InstructionWithoutDescriptionParser(_SuitesSectionParser()))


class TestSuiteSectionInstruction(TestSuiteInstruction):
    def resolve_paths(self,
                      environment: Environment) -> list:
        """
        :raises FileNotAccessibleError: A referenced file is not accessible.
        :return: [pathlib.Path]
        """
        raise NotImplementedError()


class _SuitesSectionParser(InstructionParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> TestSuiteSectionInstruction:
        line_text = rest_of_line.strip()
        return _TestSuiteWildcardFileInstruction(line_text) \
            if utils.is_wildcard_pattern(line_text) \
            else _TestSuiteNonWildcardFileInstruction(line_text)


class _TestSuiteNonWildcardFileInstruction(TestSuiteSectionInstruction):
    def __init__(self, file_name: str):
        self._file_name = file_name

    def resolve_paths(self, environment: instruction.Environment) -> list:
        return utils.resolve_non_wildcard_path(self._file_name, environment)


class _TestSuiteWildcardFileInstruction(TestSuiteSectionInstruction):
    """
    Resolves a list of paths from a file-name pattern.
    """

    def __init__(self, pattern: str):
        self._pattern = pattern

    def resolve_paths(self, environment: instruction.Environment) -> list:
        return utils.resolve_wildcard_paths(self._pattern, environment)
