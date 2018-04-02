from exactly_lib.instructions.assert_.utils.assertion_part import SequenceOfCooperativeAssertionParts, \
    AssertionInstructionFromAssertionPart, IdentityAssertionPartWithValidationAndReferences
from exactly_lib.instructions.assert_.utils.file_contents import parse_file_contents_assertion_part
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFileConstructor
from exactly_lib.instructions.assert_.utils.file_contents.parts.contents_checkers import FileExistenceAssertionPart, \
    FileConstructorAssertionPart
from exactly_lib.instructions.assert_.utils.instruction_parser import AssertPhaseInstructionTokenParser
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionSourceInfo


class ComparisonActualFileParser(Parser[ComparisonActualFileConstructor]):
    pass


class Parser(AssertPhaseInstructionTokenParser):
    """
    An instruction that

     - checks the existence of a file,
     - transform it using a given transformer
     - performs a last custom check on the transformed file
    """

    def __init__(self,
                 instruction_name: str,
                 actual_file_parser: ComparisonActualFileParser):
        self._instruction_name = instruction_name
        self._actual_file_parser = actual_file_parser

    def parse_from_token_parser(self, parser: TokenParser) -> AssertPhaseInstruction:
        source_info = InstructionSourceInfo(parser.first_line_number, self._instruction_name)
        actual_file_constructor = self._actual_file_parser.parse_from_token_parser(parser)
        actual_file_assertion_part = parse_file_contents_assertion_part.parse(parser)

        return AssertionInstructionFromAssertionPart(
            SequenceOfCooperativeAssertionParts([
                IdentityAssertionPartWithValidationAndReferences(actual_file_constructor.validator,
                                                                 actual_file_constructor.references),
                FileConstructorAssertionPart(),
                FileExistenceAssertionPart(),
                actual_file_assertion_part,
            ]),
            source_info,
            lambda env: actual_file_constructor
        )
