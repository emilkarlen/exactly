from exactly_lib.document import parse
from exactly_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SectionElementParserForStandardCommentAndEmptyLines
from exactly_lib.test_suite.instruction_set import instruction, utils
from exactly_lib.test_suite.instruction_set.instruction import Environment, TestSuiteInstruction
from exactly_lib.util import line_source


def new_parser() -> parse.SectionElementParser:
    return _CasesSectionParser()


class TestCaseSectionInstruction(TestSuiteInstruction):
    def resolve_paths(self,
                      environment: Environment) -> list:
        """
        :raises FileNotAccessibleError: A referenced file is not accessible.
        :return: [pathlib.Path]
        """
        raise NotImplementedError()


class _CasesSectionParser(SectionElementParserForStandardCommentAndEmptyLines):
    def _parse_instruction(self,
                           source: line_source.LineSequenceBuilder) -> TestCaseSectionInstruction:
        line_text = source.first_line.text
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
