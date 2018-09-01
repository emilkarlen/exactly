from pathlib import Path
from typing import List

from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionWithoutDescriptionParser, standard_syntax_element_parser, \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.section_parsing import SectionElementParser
from exactly_lib.test_suite.instruction_set import utils
from exactly_lib.test_suite.instruction_set.instruction import Environment, TestSuiteFileReferencesInstruction


def new_parser() -> SectionElementParser:
    return standard_syntax_element_parser(InstructionWithoutDescriptionParser(_CasesSectionParser()))


class CaseSectionInstruction(TestSuiteFileReferencesInstruction):
    def __init__(self, resolver: utils.FileNamesResolver):
        self._resolver = resolver

    def resolve_paths(self, environment: Environment) -> List[Path]:
        """
        :raises FileNotAccessibleError: A referenced file is not accessible.
        """
        return self._resolver.resolve(environment)


class _CasesSectionParser(InstructionParserWithoutSourceFileLocationInfo):
    def parse_from_source(self, source: ParseSource) -> CaseSectionInstruction:
        resolver = utils.parse_file_names_resolver(source)
        return CaseSectionInstruction(resolver)
