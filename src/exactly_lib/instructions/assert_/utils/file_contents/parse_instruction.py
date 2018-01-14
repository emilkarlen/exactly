from exactly_lib.instructions.assert_.utils.assertion_part import SequenceOfCooperativeAssertionParts, \
    AssertionInstructionFromAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents import parse_file_contents_assertion_part
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.parts.contents_checkers import FileExistenceAssertionPart
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction


def parse_instruction(actual_file: ComparisonActualFile,
                      token_parser: TokenParser) -> AssertPhaseInstruction:
    """
    An instruction that

     - checks the existence of a file,
     - transform it using a given transformer
     - performs a last custom check on the transformed file
    """
    actual_file_assertion_part = parse_file_contents_assertion_part.parse(token_parser)

    return AssertionInstructionFromAssertionPart(
        SequenceOfCooperativeAssertionParts([
            FileExistenceAssertionPart(actual_file),
            actual_file_assertion_part,
        ]),
        lambda env: 'initial assertion part argument - not used'
    )
